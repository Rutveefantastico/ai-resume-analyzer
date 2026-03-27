import streamlit as st
import requests
import pandas as pd
import time

from utils.parser import extract_text_from_pdf
from utils.skill_extractor import extract_skills_advanced
from utils.matcher import match_resume_job
from utils.ats_score import calculate_ats_score
from utils.gemini_ai import get_gemini_suggestions   # 👈 FREE AI
from utils.pdf_generator import create_pdf

from streamlit_lottie import st_lottie
from utils.database import create_tables, save_resume, get_user_resumes, delete_resume
from utils.image_parser import extract_text_from_image
from utils.auth import signup, login

from datetime import datetime



#----------------database setup----------------
create_tables()

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False


if "report_saved" not in st.session_state:
    st.session_state.report_saved = False

# ------------------ LOGIN / SIGNUP UI ------------------

st.markdown("""
<style>

/* -------- LANDING PAGE -------- */
.landing-container {
    text-align: center;
    padding: 60px;
    max-width: 700px;
    margin: auto;
}

.landing-text {
    width: 50%;
}

.landing-title {
    font-size: 48px;
    font-weight: bold;
}

.landing-sub {
    color: #94a3b8;
    margin-top: 10px;
}

.landing-btn {
    margin-top: 20px;
}

/* -------- SPLIT LOGIN -------- */
.auth-wrapper {
    display: flex;
    height: 80vh;
}

.auth-left {
    width: 50%;
    padding: 40px;
}

.auth-right {
    width: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* -------- FLOATING INPUT -------- */
.input-group {
    position: relative;
    margin-bottom: 20px;
}

.input-group input {
    width: 100%;
    padding: 12px;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    color: white;
}

.input-group label {
    position: absolute;
    top: 12px;
    left: 12px;
    color: #94a3b8;
    font-size: 14px;
    transition: 0.3s;
}

.input-group input:focus + label,
.input-group input:not(:placeholder-shown) + label {
    top: -8px;
    left: 10px;
    font-size: 12px;
    color: #06b6d4;
    background: #020617;
    padding: 0 5px;
}

</style>
""", unsafe_allow_html=True)



# ------------------ AUTH SYSTEM ------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------ AUTH UI ------------------

if not st.session_state.logged_in:

    from streamlit_lottie import st_lottie
    import requests

    def load_lottie(url):
        return requests.get(url).json()

    login_anim = load_lottie("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")

    st_lottie(login_anim, height=200)

    # ------------------ CSS ------------------
    st.markdown("""
    <style>

    .landing-container {
        text-align: center;
        padding: 60px;
    }

    .landing-title {
        font-size: 48px;
        font-weight: bold;
    }

    .landing-sub {
        color: #94a3b8;
        margin-top: 10px;
        font-size: 18px;
    }

    .auth-card {
        max-width: 400px;
        margin: auto;
        margin-top: 30px;
        padding: 30px;
        border-radius: 20px;
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(0,255,255,0.1);
    }

    .stTextInput input {
        background-color: #0f172a !important;
        color: white !important;
        border-radius: 8px !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # ------------------ LANDING PAGE ------------------
    st.markdown("""
    <div class="landing-container">
        <div class="landing-title">🧠 AI Resume Analyzer</div>
        <div class="landing-sub">
            Analyze your resume with AI, improve ATS score, and get hired faster 🚀
        </div>
    
    </div>
    """, unsafe_allow_html=True)

    if "show_auth" not in st.session_state:
        st.session_state.show_auth = False

    if not st.session_state.show_auth:
        if st.button("🚀 Get Started"):
            st.session_state.show_auth = True
            st.rerun()

    else:

        # ------------------ LOGIN CARD ------------------
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Login", "📝 Signup"])

        # ------------------ LOGIN ------------------
        with tab1:
            username = st.text_input(
                "👤 Username",
                key="login_user",
                placeholder="Enter your username"
            )

            show_pass = st.checkbox("👁 Show Password", key="show_login")

            password = st.text_input(
                "🔒 Password",
                type="default" if show_pass else "password",
                key="login_pass",
                placeholder="Enter your password"
            )

            if st.button("🚀 Login"):
                user = login(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login successful 🎉")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Invalid credentials ❌")

        # ------------------ SIGNUP ------------------
        with tab2:
            new_user = st.text_input(
                "👤 Create Username",
                key="signup_user",
                placeholder="Choose a username"
            )

            show_signup = st.checkbox("👁 Show Password", key="show_signup")

            new_pass = st.text_input(
                "🔒 Create Password",
                type="default" if show_signup else "password",
                key="signup_pass",
                placeholder="Create a password"
            )

            if st.button("✨ Create Account"):
                if signup(new_user, new_pass):
                    st.success("Account created 🎉")
                else:
                    st.error("User already exists")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ------------------ PAGE CONFIG ------------------

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# ------------------ LOAD LOTTIE ------------------
def load_lottie(url):
    return requests.get(url).json()

lottie = load_lottie("https://assets2.lottiefiles.com/packages/lf20_kyu7xb1v.json")

# ------------------ UI ------------------
st.markdown("""
<style>

/* Animated gradient */
body {
    background: linear-gradient(-45deg, #020617, #0f172a, #1e293b, #020617);
    background-size: 400% 400%;
    animation: gradientBG 10s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}                

/* Background */
body {
    background: linear-gradient(135deg, #020617, #0f172a, #020617);
    color: white;
}

/* Main container */
.main {
    background-color: transparent;
}                      

/* Title */
.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 30px;
}

/* Glass Card */
.card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.1);
    margin-bottom: 20px;
}
.card:hover {
    transform: translateY(-5px);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #6366f1, #06b6d4);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
    transition: 0.3s;
    font-weight: bold;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px #06b6d4;
}

  /* Input fields */
.stTextInput>div>div>input {
    background-color: #0f172a;
    color: white;
    border-radius: 8px;
}

/* File uploader */
.stFileUploader {
    background-color: #0f172a;
    border-radius: 10px;
    padding: 10px;
}

/* Skill tags */
.skill-tag {
    display: inline-block;
    background: #1e40af;
    padding: 6px 12px;
    border-radius: 8px;
    margin: 4px;
    color: white;
    font-size: 14px;
}

/* Section titles */
.section-title {
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 10px;
}
          

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #020617;
}

/* Progress */
.stProgress > div > div {
    background: linear-gradient(90deg, #22c55e, #4ade80);
}
            
/* KPI cards spacing */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 0 10px rgba(0,255,255,0.1);
}

/* Section spacing */
.block-container {
    padding-top: 2rem;
}

/* Smooth look */
h2, h3 {
    color: #e2e8f0;
}            

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyze • Optimize • Get Hired 🚀</div>', unsafe_allow_html=True)
st_lottie(lottie, height=200)

# ------------------ FEATURE HIGHLIGHTS (🔥 ADDED) ------------------
col1, col2, col3 = st.columns(3)
col1.metric("⚡ Speed", "Instant Analysis")
col2.metric("🤖 AI Powered", "Smart Suggestions")
col3.metric("📊 Accuracy", "High ATS Match")

#------------------ Logout button ------------------

st.sidebar.markdown(f"👤 Logged in as: {st.session_state.username}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ------------------ TABS ------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Analyzer", "📊 Dashboard",  "👤 My Reports", "⚙️ Profile", "⚖️ Compare"])

# ------------------ JOB ROLES ------------------
job_roles = {

    "Data Scientist": """
    Python, Machine Learning, Deep Learning, NLP, Statistics,
    Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch,
    Data Visualization, SQL, Feature Engineering, Model Deployment
    """,

    "Data Analyst": """
    Excel, SQL, Power BI, Tableau, Data Cleaning,
    Data Visualization, Statistics, Python, Pandas,
    Business Intelligence, Reporting, Dashboarding
    """,

    "Machine Learning Engineer": """
    Python, Machine Learning, Deep Learning, TensorFlow, PyTorch,
    Model Deployment, MLOps, Docker, Kubernetes,
    API Development, Feature Engineering, Cloud (AWS/GCP)
    """,

    "AI Engineer": """
    Python, NLP, Deep Learning, Transformers,
    Large Language Models, OpenAI API, Hugging Face,
    Model Fine-tuning, Vector Databases, LangChain
    """,

    "Software Engineer": """
    Data Structures, Algorithms, OOP,
    Java, Python, C++, System Design,
    Git, REST APIs, Problem Solving
    """,

    "Frontend Developer": """
    HTML, CSS, JavaScript, React.js,
    Tailwind CSS, Bootstrap, UI/UX Design,
    Responsive Design, Web Performance
    """,

    "Backend Developer": """
    Python, Node.js, Java, Spring Boot,
    REST APIs, Databases, SQL, MongoDB,
    Authentication, Microservices, API Design
    """,

    "Full Stack Developer": """
    HTML, CSS, JavaScript, React,
    Node.js, Express.js, MongoDB,
    REST APIs, Git, Deployment, System Design
    """,

    "Cloud Engineer": """
    AWS, Azure, GCP, Cloud Architecture,
    Virtualization, Networking, Docker,
    Kubernetes, CI/CD, Infrastructure as Code
    """,

    "DevOps Engineer": """
    CI/CD, Jenkins, Docker, Kubernetes,
    Linux, Shell Scripting, Monitoring,
    AWS, Git, Infrastructure Automation
    """,

    "Cyber Security Analyst": """
    Network Security, Ethical Hacking,
    Penetration Testing, Firewalls,
    IDS/IPS, Cryptography, Risk Analysis,
    Security Tools (Wireshark, Metasploit)
    """,

    "Database Administrator": """
    SQL, Database Design, Oracle,
    MySQL, PostgreSQL, Backup & Recovery,
    Performance Tuning, Data Security
    """,

    "Mobile App Developer": """
    Java, Kotlin, Swift, Flutter,
    React Native, Android Development,
    iOS Development, API Integration,
    UI/UX, Mobile Testing
    """,

    "Business Analyst": """
    Requirement Gathering, SQL,
    Data Analysis, Excel, Power BI,
    Stakeholder Communication,
    Documentation, Process Modeling
    """,

    "AI/ML Researcher": """
    Python, Deep Learning, NLP,
    Research Papers, Algorithms,
    Mathematics, Statistics,
    PyTorch, TensorFlow, Experimentation
    """
}



# ================== ANALYZER ==================

with tab1:

    # ------------------ INPUT MODE ------------------

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🎯 Choose Job Target</div>", unsafe_allow_html=True)
    mode = st.radio("Choose Input Type", ["Predefined Role", "Custom Job Description"])

    if mode == "Predefined Role":
        selected_role = st.selectbox("Select Job Role", list(job_roles.keys()))
        job_desc = job_roles[selected_role]

    else:
        job_desc = st.text_area("Paste Job Description")


    job_skills = [skill.strip().lower() for skill in job_desc.split(",")]

    # upload resume------------>>>>>>>>>>>>

    st.markdown("<div class='section-title'>📄 Upload Resume</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Resume (PDF/ JPG/ PNG)", type=["pdf", "jpg", "png"])

    # RESET STATE WHEN FILE REMOVED
    if uploaded_file is None:
        st.session_state.analysis_done = False
        st.session_state.report_saved = False

    if uploaded_file and job_desc and not st.session_state.analysis_done:

        with st.spinner("Analyzing your resume..."):
            time.sleep(2)

            if uploaded_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
                st.session_state.resume_text = resume_text

            elif uploaded_file.type in ["image/jpeg", "image/png"]:
                resume_text = extract_text_from_image(uploaded_file)
                st.session_state.resume_text = resume_text

            resume_skills = extract_skills_advanced(resume_text)

            match_score = match_resume_job(resume_text, job_desc)
            ats_score, missing_skills = calculate_ats_score(resume_skills, job_skills)

    if uploaded_file and job_desc and not st.session_state.analysis_done:

        # ✅ MARK ANALYSIS DONE
        st.session_state.analysis_done = True

        # ✅ STORE RESULTS IN SESSION
        st.session_state.match_score = match_score
        st.session_state.ats_score = ats_score
        st.session_state.resume_skills = resume_skills
        st.session_state.missing_skills = missing_skills

        # ------------------ LOAD RESULTS FROM SESSION ------------------

        if st.session_state.analysis_done:

            match_score = st.session_state.match_score
            ats_score = st.session_state.ats_score
            resume_skills = st.session_state.resume_skills
            missing_skills = st.session_state.missing_skills

        # ✅ SHOW TOAST ONLY ONCE
        st.toast("Analysis Complete 🚀")

        st.success("✅ Resume Uploaded Successfully")

        st.markdown("---")


        # ------------------ COLOR FUNCTION ------------------
        def get_color(score):
            if score > 75:
                return "#22c55e"  # green
            elif score > 50:
                return "#facc15"  # yellow
            else:
                return "#ef4444"  # red

        # ------------------ CALCULATIONS ------------------

        # Match Score (already calculated)
        match_percent = int(match_score)

        # ATS Score (already calculated)
        ats_percent = int(ats_score)

        # Keywords Found
        keywords_found = len(set(resume_skills) & set(job_skills))

        # ------------------ KPI CARDS ------------------

        match_color = get_color(match_percent)
        ats_color = get_color(ats_percent)
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class='card'>
                <h3>Match Score</h3>
                <h2 style="color:{match_color}">{match_percent}%</h2>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class='card'>
                <h3> ATS Score</h3>
                <h2 style="color:{ats_color}">{ats_percent}%</h2>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class='card'>
                <h3>Keywords Found</h3>
                <h2>{keywords_found}</h2>
            </div>
            """, unsafe_allow_html=True)

        # ------------------ EXTRACTED SKILLS ------------------

        st.markdown("<div class='section-title'>⭐ Extracted Skills</div>", unsafe_allow_html=True)

        skill_html = ""
        for skill in resume_skills:
            skill_html += f"<span class='skill-tag'>{skill}</span>"

        st.markdown(skill_html, unsafe_allow_html=True)

        # ------------------ MISSING SKILLS ------------------

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🧩 Missing Skills</div>", unsafe_allow_html=True)

        missing_html = ""
        for skill in missing_skills:
            missing_html += f"<span style='background:#ef4444;padding:6px 10px;border-radius:8px;margin:4px;display:inline-block;color:white;'>{skill}</span>"

        st.markdown(missing_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ------------------ DIVIDER ------------------
        st.divider()

        # ------------------ CTA SECTION (🔥 ADDED) ------------------
        st.markdown("""
        <div class="card">
        <h3>🚀 Improve Your Resume Now</h3>
        <p>Get AI-powered suggestions and increase your chances of getting hired.</p>
        </div>
        """, unsafe_allow_html=True)

        # ------------------ AI SUGGESTIONS ------------------
   

    

    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""

    if "suggestions" not in st.session_state:
        st.session_state.suggestions = ""

    with st.container():    
        if st.button("💡 Get AI Suggestions"):

            if st.session_state.get("resume_text"):

                result = get_gemini_suggestions(
                    st.session_state.resume_text, job_desc
                )

                

                st.session_state.suggestions = result

            else:
                st.warning("⚠️ Please analyze resume first")

        if st.session_state.suggestions:
                st.markdown(f"<div class='card'><h3>🤖 AI Analysis</h3><p>{st.session_state.suggestions}</p></div>", unsafe_allow_html=True)

        

        # ------------------ SAVE TO DATABASE ------------------
        
        if st.session_state.analysis_done and not st.session_state.report_saved:

            save_resume(
                st.session_state.username,
                match_score,
                ats_score,
                resume_skills,
                missing_skills,
                st.session_state.suggestions
            )

            st.session_state.report_saved = True
            
        
        
        # ------------------ DOWNLOAD ------------------
        if st.button("📥 Download Report"):

            if st.session_state.analysis_done:

                file_path = "resume_report.pdf"

                create_pdf(
                    file_path,
                    st.session_state.match_score,
                    st.session_state.ats_score,
                    st.session_state.resume_skills,
                    st.session_state.missing_skills,
                    st.session_state.suggestions
                )

                with open(file_path, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name="resume_report.pdf",
                        mime="application/pdf"
                    )
            else:
                st.warning("⚠️ Analyze resume first")

# ================== DASHBOARD ==================
with tab2:
    if st.session_state.analysis_done:

        resume_skills = st.session_state.resume_skills
        job_skills =job_skills  # already exists

        matched = len(set(resume_skills) & set(job_skills))
        missing = len(set(job_skills) - set(resume_skills))

        df = pd.DataFrame({
            "Category": ["Matched Skills", "Missing Skills"],
            "Count": [matched, missing]
        })

        st.bar_chart(df.set_index("Category"))

# ================== JOBS ==================
with tab3:
    st.markdown("## 📂 Your Previous Reports")

    user_data = get_user_resumes(st.session_state.username)

    if user_data:
        for data in user_data:
            report_id = data[0] 
            created_at = data[7]   # 👈 timestamp column

            col1, col2, col3 = st.columns([1, 3, 1])
            
            #KPI
            with col1:
                st.metric("Match %", f"{data[2]}%")
                st.metric("ATS %", f"{data[3]}%")

            # Details
            with col2:
                st.markdown(f"""
                <div class="card">
                    <h4>🧠 Skills Extracted</h4>
                    <p>{data[4]}</p>
                    <p style="color:#94a3b8; font-size:12px;">
                        📅 Generated on: {created_at}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # DELETE BUTTON
            with col3:
                if st.button("🗑 Delete", key=f"delete_{report_id}"):

                    delete_resume(report_id)

                    # PREVENT RE-ANALYSIS ON RERUN
                    st.session_state.analysis_done = True

                    st.toast("Report deleted ❌")
                    st.rerun()


            st.markdown("---")
    else:
        st.info("No reports yet")



with tab4:
    st.subheader("⚙️ User Profile")

    st.markdown(f"""
    <div class="card">
    <h3>👤 Username: {st.session_state.username}</h3>
    <p>📊 Total Reports Generated: {len(get_user_resumes(st.session_state.username))}</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("More features coming soon: profile edit, password change, etc.")

with tab5:
    st.subheader("⚖️ Compare Two Resumes")

    col1, col2 = st.columns(2)

    with col1:
        file1 = st.file_uploader("Upload Resume 1", type=["pdf", "jpg", "png"], key="r1")

    with col2:
        file2 = st.file_uploader("Upload Resume 2", type=["pdf", "jpg", "png"], key="r2")

    if file1 and file2 and job_desc:

        if file1.type == "application/pdf":
            text1 = extract_text_from_pdf(file1)
        elif file1.type in ["image/jpeg", "image/png"]:
            text1 = extract_text_from_image(file1)

        if file2.type == "application/pdf":
            text2 = extract_text_from_pdf(file2)
        elif file2.type in ["image/jpeg", "image/png"]:
            text2 = extract_text_from_image(file2)

        skills1 = extract_skills_advanced(text1)
        skills2 = extract_skills_advanced(text2)

        score1 = match_resume_job(text1, job_desc)
        score2 = match_resume_job(text2, job_desc)

        st.subheader("📊 Comparison Result")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"<div class='card'><h3>Resume 1</h3><h2>{score1}%</h2></div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='card'><h3>Resume 2</h3><h2>{score2}%</h2></div>", unsafe_allow_html=True)

        # Winner logic
        if score1 > score2:
            st.success("🏆 Resume 1 is better matched!")
        elif score2 > score1:
            st.success("🏆 Resume 2 is better matched!")
        else:
            st.info("🤝 Both resumes are equally matched!")

        # Skill difference
        st.subheader("🧠 Skill Comparison")

        st.write("Only in Resume 1:", list(set(skills1) - set(skills2)))
        st.write("Only in Resume 2:", list(set(skills2) - set(skills1)))










