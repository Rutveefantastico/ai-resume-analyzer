from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def match_resume_job(resume_text, job_desc):
    cv = CountVectorizer().fit_transform([resume_text, job_desc])
    similarity = cosine_similarity(cv)[0][1]
    return round(similarity * 100, 2)