import ijson
from app.scripts.ingest import clean_record
from app.services.embeddings import get_embedding
from app.services.enrichment import enrich_job
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "jobs_raw.json"

with open(DATA_PATH, "rb") as f:
    count = 0
    for record in ijson.items(f, "item"):
        cleaned = clean_record(record)
        if cleaned is None:
            print("SKIPPED (invalid):", record.get("title"))
            continue

        print("\n--- Job:", cleaned["title"], "---")
        embedding = get_embedding(f"{cleaned['title']} {cleaned['description']}")
        print("Embedding length:", len(embedding) if embedding else None)

        enrichment = enrich_job(cleaned["title"], cleaned["description"])
        print("Tags:", enrichment["tags"])
        print("Role:", enrichment["role_category"])
        print("Experience:", enrichment["experience_required"])

        count += 1
        if count >= 3:
            break