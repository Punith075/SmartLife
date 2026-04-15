import os
import re
import time
import tempfile
from io import BytesIO
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
from pypdf import PdfReader

try:
    from androguard.misc import AnalyzeAPK
    APK_ANALYSIS_AVAILABLE = True
except Exception:
    APK_ANALYSIS_AVAILABLE = False


# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(
    page_title="SmartLife AI+",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------
# LOAD ENV
# ------------------------
load_dotenv(dotenv_path=".env", override=True)
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("Groq API key not found. Please check your .env file.")
    st.stop()

try:
    client = Groq(api_key=groq_api_key)
except Exception as e:
    st.error(f"Groq setup error: {e}")
    st.stop()

# ------------------------
# SESSION STATE
# ------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ------------------------
# GLOBAL STYLES
# ------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(99,102,241,0.20), transparent 24%),
        radial-gradient(circle at top right, rgba(6,182,212,0.16), transparent 24%),
        linear-gradient(135deg, #071120 0%, #0b1730 45%, #091833 100%);
    color: #f8fbff;
}

header, footer {
    visibility: hidden;
}

.stDeployButton {
    display: none;
}

.block-container {
    max-width: 1220px;
    padding-top: 0.6rem;
    padding-bottom: 1rem;
}

.section-wrap {
    background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 28px;
    padding: 28px 24px 22px 24px;
    box-shadow: 0 18px 50px rgba(0,0,0,0.22);
    backdrop-filter: blur(16px);
    margin-top: 1rem;
}

.section-title {
    font-size: 1.85rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.35rem;
}

.section-caption {
    color: #dbe5ff;
    font-size: 1rem;
    margin-bottom: 1rem;
}

.small-help {
    color: #d6e0ff;
    font-size: 0.92rem;
}

.hero {
    text-align: center;
    padding: 28px 12px 12px 12px;
}

.hero-title {
    font-size: 4rem;
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -2px;
    color: white;
    margin-bottom: 10px;
}

.hero-highlight,
.login-title span {
    background: linear-gradient(90deg, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    max-width: 850px;
    margin: 0 auto;
    color: #c8d5ff;
    font-size: 1.08rem;
    line-height: 1.7;
}

.hero-chip-row {
    margin-top: 18px;
}

.hero-chip,
.login-chip {
    display: inline-block;
    padding: 9px 15px;
    margin: 6px;
    border-radius: 999px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.10);
    color: #e8efff;
    font-weight: 600;
    font-size: 0.92rem;
}

.feature-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.05));
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 26px;
    padding: 24px 20px;
    min-height: 310px;
    box-shadow: 0 14px 32px rgba(0,0,0,0.18);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    backdrop-filter: blur(12px);
}

.feature-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 38px rgba(0,0,0,0.24);
    border-color: rgba(103, 232, 249, 0.35);
}

.feature-icon {
    font-size: 2.3rem;
    margin-bottom: 10px;
}

.feature-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: white;
    margin-bottom: 8px;
}

.feature-desc {
    color: #d5def8;
    font-size: 0.98rem;
    line-height: 1.65;
    min-height: 92px;
}

.feature-points {
    color: #eef4ff;
    font-size: 0.92rem;
    line-height: 1.7;
    margin-top: 10px;
}

.stButton > button {
    width: 100%;
    border: 0 !important;
    border-radius: 15px !important;
    padding: 0.82rem 1rem !important;
    font-weight: 800 !important;
    color: white !important;
    background: linear-gradient(90deg, #4f46e5, #06b6d4) !important;
    box-shadow: 0 10px 22px rgba(79,70,229,0.30);
}

.stButton > button:hover {
    filter: brightness(1.06);
}

div[data-testid="stWidgetLabel"] label p,
div[data-testid="stWidgetLabel"] p,
div[data-testid="stFileUploaderDropzoneInstructions"],
div[data-testid="stFileUploaderDropzone"] small,
div[data-testid="stFileUploader"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label {
    color: #eef2ff !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.95) !important;
    color: #111827 !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 14px !important;
    font-size: 1rem !important;
}

div[data-testid="stTextArea"] textarea::placeholder,
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stNumberInput"] input::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.95) !important;
    color: #111827 !important;
    border-radius: 14px !important;
}

div[data-testid="stSelectbox"] * {
    color: #111827 !important;
}

div[data-testid="stFileUploader"] section {
    background: rgba(255,255,255,0.08);
    border: 1px dashed rgba(255,255,255,0.28);
    border-radius: 16px;
    padding: 16px !important;
}

div[data-testid="stFileUploader"] button {
    background: #ffffff !important;
    color: #111827 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    border: none !important;
}

div[data-testid="stFileUploader"] button span {
    color: #111827 !important;
}

div[data-testid="stFileUploaderDropzoneInstructions"] span,
div[data-testid="stFileUploaderDropzoneInstructions"] small,
div[data-testid="stFileUploader"] span,
div[data-testid="stFileUploader"] small {
    color: #eef2ff !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

.result-shell {
    margin-top: 16px;
    border-radius: 18px;
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.10);
}

.result-shell * {
    color: #ffffff !important;
}

.result-safe {
    background: linear-gradient(135deg, rgba(22,163,74,0.24), rgba(34,197,94,0.12));
    border: 1px solid rgba(74,222,128,0.32);
}

.result-scam {
    background: linear-gradient(135deg, rgba(220,38,38,0.24), rgba(248,113,113,0.12));
    border: 1px solid rgba(252,165,165,0.32);
}

.result-normal {
    background: linear-gradient(135deg, rgba(59,130,246,0.18), rgba(99,102,241,0.10));
    border: 1px solid rgba(147,197,253,0.25);
}

.loading-box {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 18px;
    margin-top: 12px;
    margin-bottom: 10px;
    color: #ffffff;
}

.loading-bar {
    height: 10px;
    border-radius: 999px;
    overflow: hidden;
    background: rgba(255,255,255,0.08);
    margin-top: 10px;
}

.loading-fill {
    width: 40%;
    height: 100%;
    background: linear-gradient(90deg, #4f46e5, #06b6d4, #4f46e5);
    background-size: 200% 100%;
    animation: moveBar 1.4s linear infinite;
    border-radius: 999px;
}

@keyframes moveBar {
    0% { transform: translateX(-80%); }
    100% { transform: translateX(250%); }
}

.voice-title {
    margin-top: 14px;
    color: #eef2ff;
    font-weight: 700;
}

.footer-note {
    text-align: center;
    color: #b7c2e0;
    margin-top: 22px;
    font-size: 0.95rem;
}

.back-btn-note {
    color: #dbe5ff;
    margin-bottom: 8px;
}

.login-title {
    font-size: 4rem;
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -2px;
    margin-bottom: 16px;
    color: #ffffff;
}

.login-badge {
    display: inline-block;
    padding: 10px 16px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.14);
    color: #dbeafe;
    font-weight: 700;
    font-size: 0.88rem;
    margin-bottom: 18px;
}

.login-sub {
    color: #cbd5e1;
    font-size: 1.05rem;
    line-height: 1.9;
    max-width: 560px;
    margin-bottom: 20px;
}

.orb-box {
    margin-top: 24px;
    height: 220px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}

.orb-core {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #67e8f9, #4f46e5 70%, #1e1b4b 100%);
    box-shadow:
        0 0 45px rgba(79,70,229,0.65),
        0 0 100px rgba(6,182,212,0.35),
        0 0 180px rgba(99,102,241,0.28);
    animation: pulseGlow 2.8s ease-in-out infinite;
    position: relative;
}

.orb-core::before {
    content: "";
    position: absolute;
    inset: -22px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.14);
    animation: spinRing 9s linear infinite;
}

.orb-core::after {
    content: "";
    position: absolute;
    inset: -45px;
    border-radius: 50%;
    border: 1px solid rgba(103,232,249,0.18);
    animation: spinRing 12s linear infinite reverse;
}

.orb-label {
    position: absolute;
    bottom: 0;
    color: #dbeafe;
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.4px;
}

@keyframes pulseGlow {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.06); }
}

@keyframes spinRing {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.login-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.11), rgba(255,255,255,0.06));
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 28px;
    padding: 30px 26px 24px 26px;
    box-shadow: 0 18px 50px rgba(0,0,0,0.28);
    backdrop-filter: blur(16px);
    margin-top: 34px;
}

.login-card-title {
    font-size: 2.2rem;
    color: white;
    font-weight: 800;
    margin-bottom: 10px;
}

.login-card-text {
    color: #cbd5e1;
    line-height: 1.8;
    margin-bottom: 20px;
    font-size: 1rem;
}

.login-note {
    margin-top: 14px;
    color: #94a3b8;
    font-size: 0.9rem;
}

@media (max-width: 900px) {
    .login-title,
    .hero-title {
        font-size: 2.8rem;
    }
    .login-card {
        margin-top: 10px;
    }
}
</style>
""", unsafe_allow_html=True)


# ------------------------
# HELPERS
# ------------------------
def go_to(page_name: str) -> None:
    st.session_state.page = page_name


def do_logout() -> None:
    st.session_state.logged_in = False
    st.session_state.page = "landing"


def generate_ai(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a clear, practical, premium AI assistant. Always respond in clean markdown."
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=1400,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠ AI error: {e}"


def extract_pdf_text(uploaded_file) -> str:
    try:
        reader = PdfReader(uploaded_file)
        text_chunks = []
        for page in reader.pages:
            text_chunks.append(page.extract_text() or "")
        return "\n".join(text_chunks).strip()
    except Exception as e:
        return f"PDF extraction failed: {e}"


def analyze_apk(uploaded_file) -> str:
    if not APK_ANALYSIS_AVAILABLE:
        return "APK analysis library not installed. Install androguard."

    temp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".apk") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        a, d, dx = AnalyzeAPK(temp_path)

        permissions = a.get_permissions()
        package_name = a.get_package()
        app_name = a.get_app_name()
        min_sdk = a.get_min_sdk_version()
        target_sdk = a.get_target_sdk_version()

        suspicious_permissions = [
            p for p in permissions
            if any(key in p.upper() for key in [
                "READ_SMS", "SEND_SMS", "RECEIVE_SMS", "READ_CONTACTS",
                "READ_CALL_LOG", "WRITE_CALL_LOG", "RECORD_AUDIO",
                "READ_PHONE_STATE", "REQUEST_INSTALL_PACKAGES",
                "SYSTEM_ALERT_WINDOW", "ACCESS_FINE_LOCATION"
            ])
        ]

        return f"""
APK File Summary

App Name: {app_name}
Package Name: {package_name}
Min SDK: {min_sdk}
Target SDK: {target_sdk}

Permissions:
{chr(10).join(f"- {p}" for p in permissions[:30]) if permissions else "- None found"}

Suspicious / High-Risk Permissions:
{chr(10).join(f"- {p}" for p in suspicious_permissions) if suspicious_permissions else "- None detected"}
""".strip()

    except Exception as e:
        return f"APK analysis failed: {e}"
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def render_result_box(content: str, variant: str = "normal") -> None:
    css_class = {
        "safe": "result-safe",
        "scam": "result-scam",
        "normal": "result-normal"
    }.get(variant, "result-normal")

    st.markdown(f'<div class="result-shell {css_class}">', unsafe_allow_html=True)
    st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)


def extract_risk_score(text: str) -> int:
    patterns = [
        r"Risk Score\s*[:\-]?\s*(\d+)",
        r"score\s*[:\-]?\s*(\d+)",
        r"(\d+)\s*/\s*100"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            return max(0, min(100, value))
    return 50


def parse_verdict_variant(text: str) -> str:
    upper = text.upper()
    if "SCAM" in upper or "HIGH RISK" in upper:
        return "scam"
    if "SAFE" in upper:
        return "safe"
    return "normal"


def show_loading(message: str):
    st.markdown(f"""
    <div class="loading-box">
        <div>{message}</div>
        <div class="loading-bar"><div class="loading-fill"></div></div>
    </div>
    """, unsafe_allow_html=True)


def text_to_speech_bytes(text: str) -> bytes:
    clean = re.sub(r"[#*_>`]", "", text)
    clean = clean.replace("\n", " ")
    tts = gTTS(text=clean[:3500], lang="en")
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()


def calculate_bmi(weight_kg: float, height_cm: float):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return round(bmi, 2), category


def show_login_page():
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown('<div class="login-badge">SMARTLIFE AI+ • SECURE ACCESS</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Welcome to <span>SmartLife AI+</span></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="login-sub">Your premium AI assistant for fraud protection, smart daily planning, and BMI-based health guidance. Sign in to continue into your personalized AI workspace.</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<span class="login-chip">🛡 Fraud Detection</span>'
            '<span class="login-chip">🧠 Smart Advice</span>'
            '<span class="login-chip">💪 Health Guide</span>'
            '<span class="login-chip">🔊 Voice Output</span>',
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <div class="orb-box">
                <div class="orb-core"></div>
                <div class="orb-label">AI Core Active</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with right:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="login-card-title">Sign In</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="login-card-text">Access your secure SmartLife dashboard and continue with AI-powered safety, productivity, and wellness tools.</div>',
            unsafe_allow_html=True
        )

        username = st.text_input("Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("Password", placeholder="Enter your password", type="password", key="login_pass")
        login_clicked = st.button("Enter SmartLife AI+")

        st.markdown(
            '<div class="login-note">Demo login: Username <b>smartlife</b> & Password <b>demo123</b></div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if login_clicked:
            if username == "smartlife" and password == "demo123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password.")


# ------------------------
# LOGIN GATE
# ------------------------
if not st.session_state.logged_in:
    show_login_page()
    st.stop()


# ------------------------
# TOP RIGHT LOGOUT
# ------------------------
top1, top2 = st.columns([8, 1])
with top2:
    st.button("Logout", on_click=do_logout)


# ------------------------
# HERO / LANDING
# ------------------------
if st.session_state.page == "landing":
    st.markdown("""
    <div class="hero">
        <div class="hero-title">
            Meet <span class="hero-highlight">SmartLife AI+</span>
        </div>
        <div class="hero-subtitle">
            A next-generation AI assistant that helps users stay safer, plan smarter, and live healthier —
            combining fraud intelligence, daily life guidance, and BMI-based wellness insights in one premium platform.
        </div>
        <div class="hero-chip-row">
            <span class="hero-chip">🛡 Fraud Detection</span>
            <span class="hero-chip">🧠 Smart Advice</span>
            <span class="hero-chip">💪 Health Guide</span>
            <span class="hero-chip">📄 PDF Analysis</span>
            <span class="hero-chip">📱 APK Review</span>
            <span class="hero-chip">🔊 Voice Output</span>
            <span class="hero-chip">📊 Risk Meter</span>
            <span class="hero-chip">⚖ BMI Check</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
    st.markdown("## Explore Modules")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🛡</div>
            <div class="feature-title">Fraud Detection</div>
            <div class="feature-desc">
                Detect suspicious messages, risky links, fraudulent documents, and potentially unsafe APK files using AI-powered analysis.
            </div>
            <div class="feature-points">
                • Text + URL analysis<br>
                • PDF document scanning<br>
                • APK static review<br>
                • Fraud risk score meter
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open Fraud Detection", use_container_width=True, on_click=go_to, args=("fraud",))

    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Smart Advice</div>
            <div class="feature-desc">
                Get clean, structured guidance for productivity, routines, studies, planning, and everyday decision making.
            </div>
            <div class="feature-points">
                • Timetable generation<br>
                • Practical planning advice<br>
                • Motivational guidance<br>
                • Voice-enabled responses
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open Smart Advice", use_container_width=True, on_click=go_to, args=("advice",))

    with c3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💪</div>
            <div class="feature-title">Health Guide</div>
            <div class="feature-desc">
                Calculate BMI, identify whether a user is underweight, normal, overweight, or obese, and generate a health plan.
            </div>
            <div class="feature-points">
                • Weight + height inputs<br>
                • BMI calculation<br>
                • Obesity classification<br>
                • Personalized wellness plan
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open Health Guide", use_container_width=True, on_click=go_to, args=("health",))

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "fraud":
    st.markdown('<div class="back-btn-note">← Use the button below to return to the landing page</div>', unsafe_allow_html=True)
    st.button("Back to Home", on_click=go_to, args=("landing",))
    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛡 Fraud Detection</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Analyze suspicious text, links, PDF documents, or APK files with AI-powered fraud assessment.</div>',
        unsafe_allow_html=True
    )

    fraud_text = st.text_area(
        "Paste suspicious message / email / URL",
        placeholder="Example: Your bank account will be blocked. Click this link now to verify your KYC.",
        height=170
    )

    fraud_file = st.file_uploader("Upload PDF or APK", type=["pdf", "apk"])
    st.markdown(
        '<div class="small-help">PDF files are summarized. APK files are checked using static analysis.</div>',
        unsafe_allow_html=True
    )

    if st.button("Analyze Fraud Risk"):
        combined_input = ""

        if fraud_text.strip():
            combined_input += f"User Submitted Text / Link:\n{fraud_text.strip()}\n\n"

        if fraud_file is not None:
            file_name = fraud_file.name.lower()
            if file_name.endswith(".pdf"):
                pdf_text = extract_pdf_text(fraud_file)
                combined_input += f"Extracted PDF Content:\n{pdf_text[:12000]}\n\n"
            elif file_name.endswith(".apk"):
                apk_summary = analyze_apk(fraud_file)
                combined_input += f"APK Static Analysis Summary:\n{apk_summary}\n\n"

        if not combined_input.strip():
            st.warning("Please paste text/link or upload a PDF/APK file.")
        else:
            loading_placeholder = st.empty()
            with loading_placeholder.container():
                show_loading("Scanning content and calculating fraud risk...")
            time.sleep(1)

            fraud_prompt = f"""
You are an expert cyber safety and fraud detection assistant.

Analyze the provided content and determine whether it appears SAFE, SUSPICIOUS, or SCAM / HIGH RISK.

Return the answer in this exact format:

## Verdict
SAFE / SUSPICIOUS / SCAM

## Risk Score
Give only a number out of 100

## Why
- point 1
- point 2
- point 3

## What the user should do
- point 1
- point 2
- point 3

## Final advice
One short concluding line.

If analyzing an APK, comment on risky permissions and suspicious app behavior.
If evidence is limited, say that clearly.

Content to analyze:
{combined_input}
"""
            result = generate_ai(fraud_prompt)
            loading_placeholder.empty()

            if result.startswith("⚠ AI error:"):
                st.error(result)
            else:
                score = extract_risk_score(result)
                variant = parse_verdict_variant(result)

                st.subheader("📊 Fraud Risk Meter")
                st.progress(score / 100)
                r1, r2 = st.columns(2)
                r1.metric("Risk Score", f"{score}/100")
                r2.metric("Verdict", "SCAM" if variant == "scam" else "SAFE" if variant == "safe" else "SUSPICIOUS")

                render_result_box(result, variant)
                st.markdown('<div class="voice-title">🔊 Voice Output</div>', unsafe_allow_html=True)
                st.audio(text_to_speech_bytes(result), format="audio/mp3")

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "advice":
    st.markdown('<div class="back-btn-note">← Use the button below to return to the landing page</div>', unsafe_allow_html=True)
    st.button("Back to Home", on_click=go_to, args=("landing",))
    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧠 Smart Advice</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Ask about your routine, productivity, studies, or daily planning and get a clean AI response.</div>',
        unsafe_allow_html=True
    )

    advice_input = st.text_area(
        "Ask your question",
        placeholder="Example: I wake up at 6, college starts at 8:30, gym after college, homework in the evening. Make a timetable for me.",
        height=170
    )

    advice_style = st.selectbox(
        "Response style",
        ["Balanced", "Short and Direct", "Detailed Planner", "Motivational"]
    )

    if st.button("Generate Smart Advice"):
        if not advice_input.strip():
            st.warning("Please enter your question.")
        else:
            loading_placeholder = st.empty()
            with loading_placeholder.container():
                show_loading("Building your personalized plan...")
            time.sleep(1)

            advice_prompt = f"""
You are a premium life-planning assistant.

User request:
{advice_input}

Response style: {advice_style}

Return the answer in clean markdown only.
Use exactly this format:

## Clear Answer
2 to 4 lines

## Action Plan
- bullet 1
- bullet 2
- bullet 3
- bullet 4
- bullet 5

## Why this works
2 to 3 lines

## Motivation
1 short line

Keep it practical, structured, and easy to read.
"""
            result = generate_ai(advice_prompt)
            loading_placeholder.empty()

            if result.startswith("⚠ AI error:"):
                st.error(result)
            else:
                render_result_box(result, "normal")
                st.markdown('<div class="voice-title">🔊 Voice Output</div>', unsafe_allow_html=True)
                st.audio(text_to_speech_bytes(result), format="audio/mp3")

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "health":
    st.markdown('<div class="back-btn-note">← Use the button below to return to the landing page</div>', unsafe_allow_html=True)
    st.button("Back to Home", on_click=go_to, args=("landing",))
    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💪 Health Guide</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Check BMI, understand your health category, and get a personalized beginner-friendly wellness plan.</div>',
        unsafe_allow_html=True
    )

    hc1, hc2 = st.columns(2)

    with hc1:
        weight = st.number_input("Enter your weight (kg)", min_value=20.0, max_value=300.0, value=60.0, step=0.5)
        height = st.number_input("Enter your height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)

    with hc2:
        age = st.number_input("Enter your age", min_value=10, max_value=100, value=18, step=1)
        diet_pref = st.selectbox("Diet preference", ["Vegetarian", "Non-Vegetarian", "Mixed"])

    goal = st.selectbox("Select your goal", ["Weight Loss", "Muscle Gain", "Stay Fit", "Increase Energy"])

    if st.button("Generate Health Plan"):
        bmi, category = calculate_bmi(weight, height)

        st.subheader("📊 BMI Analysis")
        h1, h2 = st.columns(2)
        h1.metric("BMI", f"{bmi}")
        h2.metric("Category", category)

        if category == "Underweight":
            st.warning("You are currently in the underweight range.")
        elif category == "Normal weight":
            st.success("You are currently in the normal weight range.")
        elif category == "Overweight":
            st.warning("You are currently in the overweight range.")
        else:
            st.error("You are currently in the obese range.")

        loading_placeholder = st.empty()
        with loading_placeholder.container():
            show_loading("Analyzing BMI and creating your health plan...")
        time.sleep(1)

        health_prompt = f"""
You are a smart beginner-friendly health coach.

User details:
- Age: {age}
- Weight: {weight} kg
- Height: {height} cm
- BMI: {bmi}
- BMI Category: {category}
- Goal: {goal}
- Diet Preference: {diet_pref}

Return the answer in neat markdown with this exact format:

## Health Status
Explain what the BMI category means in 2 to 3 lines.

## Daily Routine
- bullet 1
- bullet 2
- bullet 3
- bullet 4

## Meal Suggestion
- breakfast
- lunch
- snacks
- dinner

## Workout Idea
- bullet 1
- bullet 2
- bullet 3

## Recommendation
Give a short recommendation based on whether the user is underweight, normal, overweight, or obese.

## Caution
Give 1 short safe note.

Keep it realistic, short, and beginner-friendly.
Do not give unsafe medical advice.
"""
        result = generate_ai(health_prompt)
        loading_placeholder.empty()

        if result.startswith("⚠ AI error:"):
            st.error(result)
        else:
            render_result_box(result, "normal")
            st.markdown('<div class="voice-title">🔊 Voice Output</div>', unsafe_allow_html=True)
            st.audio(text_to_speech_bytes(result), format="audio/mp3")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="footer-note">Built for AI for Impact • SmartLife AI+ delivers safety, productivity, and wellness in one premium AI experience</div>',
    unsafe_allow_html=True
)