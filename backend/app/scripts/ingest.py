import ijson
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Job
from app.services.dedup import compute_content_hash
from app.services.embeddings import get_embedding
from app.services.enrichment import enrich_job
import time

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "jobs_raw.json"

# Only this many jobs get LLM-based enrichment (tags/role/experience),
# due to API rate limits at 56k+ records. Every job still gets a local
# embedding, so semantic search/recommendations cover the full dataset.
ENRICHMENT_LIMIT = 200


def load_raw_jobs_streaming():
    with open(DATA_PATH, "rb") as f:
        for record in ijson.items(f, "item"):
            yield record

def clean_record(raw: dict) -> dict | None:
    title = raw.get("title")
    company = raw.get("company_name")
    description = raw.get("description")

    if not title or not company or not description:
        return None

    via_raw = raw.get("via", "")
    source = via_raw.replace("via ", "").strip() if via_raw else "Unknown"

    min_exp = raw.get("minExperienceRequired")
    max_exp = raw.get("maxExperienceRequired")
    if min_exp and max_exp:
        experience_required = f"{min_exp}-{max_exp} years"
    elif min_exp:
        experience_required = f"{min_exp}+ years"
    else:
        experience_required = "Not specified"

    existing_skills_raw = raw.get("skills", "")
    existing_skills = (
        [s.strip() for s in existing_skills_raw.split(",") if s.strip()]
        if existing_skills_raw else []
    )

    return {
        "source": source,
        "title": title.strip(),
        "company": company.strip(),
        "location": (raw.get("location") or "Not specified").strip(),
        "description": description.strip(),
        "experience_required": experience_required,
        "existing_skills": existing_skills,
    }

def ingest():
    db: Session = SessionLocal()

    # Load all existing hashes into memory once — O(1) duplicate lookups
    # instead of a DB round-trip per record. Empty on first run.
    existing_hashes = {h for (h,) in db.query(Job.content_hash).all()}
    print(f"Loaded {len(existing_hashes)} existing hashes.")

    inserted, skipped_invalid, skipped_duplicate, enriched_count = 0, 0, 0, 0
    batch = []
    BATCH_SIZE = 500  # commit in batches, not one-by-one, not all 56k at once

    try:
        for raw in load_raw_jobs_streaming():
            cleaned = clean_record(raw)
            if cleaned is None:
                skipped_invalid += 1
                continue

            content_hash = compute_content_hash(
                cleaned["title"], cleaned["company"], cleaned["location"]
            )

            if content_hash in existing_hashes:
                skipped_duplicate += 1
                continue
            existing_hashes.add(content_hash)  # prevents dupes within this same run too

            embedding = get_embedding(f"{cleaned['title']} {cleaned['description']}")

            # Only enrich via LLM for the first ENRICHMENT_LIMIT jobs.
            # Beyond that, fall back to the dataset's own 'skills' field
            # so every job still has usable tags, just not LLM-verified ones.
            if enriched_count < ENRICHMENT_LIMIT:
                enrichment, success = enrich_job(cleaned["title"], cleaned["description"])
                if success:
                    enriched_count += 1   # only count real successes toward the limit
                time.sleep(4)
            else:
                enrichment = {...}

            job = Job(
                source=cleaned["source"],
                title=cleaned["title"],
                company=cleaned["company"],
                location=cleaned["location"],
                description=cleaned["description"],
                experience_required=enrichment.get("experience_required", cleaned["experience_required"]),
                content_hash=content_hash,
                tags=enrichment["tags"],
                role_category=enrichment["role_category"],
                embedding=embedding,
            )
            batch.append(job)
            inserted += 1

            if len(batch) >= BATCH_SIZE:
                db.bulk_save_objects(batch)
                db.commit()
                print(f"Committed batch. Total inserted so far: {inserted}")
                batch = []

        if batch:  # commit any remainder
            db.bulk_save_objects(batch)
            db.commit()

    finally:
        db.close()

    print(f"Done. Inserted: {inserted}, Skipped invalid: {skipped_invalid}, "
          f"Skipped duplicate: {skipped_duplicate}, LLM-enriched: {enriched_count}")

if __name__ == "__main__":
    ingest()