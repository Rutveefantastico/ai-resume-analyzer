import spacy

nlp = spacy.load("en_core_web_sm")

# Load predefined skills
def load_skills():
    with open("data/skills.txt", "r") as f:
        skills = f.read().splitlines()
    return [skill.lower() for skill in skills]

def extract_skills_advanced(text):
    skills_db = load_skills()
    text = text.lower()

    found = []

    for skill in skills_db:
        if skill in text:
            found.append(skill)

    return list(set(found))