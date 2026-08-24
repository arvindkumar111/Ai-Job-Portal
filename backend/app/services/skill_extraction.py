import re

# A reference vocabulary of common tech/professional skills to match against.
# Not exhaustive — this is a deliberate, explainable tradeoff: fast, free,
# zero API dependency, at the cost of only catching skills in this list
# (won't catch a skill phrased in a way not in the vocabulary, or a skill
# genuinely outside this list).
KNOWN_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "R", "SQL",
    "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "FastAPI", "Spring",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Data Science",
    "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy", "Keras",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD", "Jenkins",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
    "Git", "GitHub", "REST API", "GraphQL", "Microservices",
    "HTML", "CSS", "Tailwind", "Bootstrap",
    "Excel", "Power BI", "Tableau", "SQL Server",
    "Agile", "Scrum", "Project Management",
    "Data Analysis", "Data Visualization", "Statistics", "A/B Testing",
    # extend as needed — this list is the primary lever for extraction quality
]

def extract_skills_from_text(text: str) -> list[str]:
    """Matches known skills against resume text using word-boundary regex,
    so 'R' doesn't match inside 'Marketing', 'Go' doesn't match inside
    'Google', etc. Case-insensitive."""
    if not text:
        return []

    found = []
    text_lower = text.lower()

    for skill in KNOWN_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)

    return found