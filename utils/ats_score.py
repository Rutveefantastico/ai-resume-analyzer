def calculate_ats_score(resume_skills, job_skills):
    matched = set(resume_skills) & set(job_skills)
    score = (len(matched) / len(job_skills)) * 100 if job_skills else 0
    return round(score, 2), list(set(job_skills) - set(resume_skills))