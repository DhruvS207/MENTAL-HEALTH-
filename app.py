import smtplib
from datetime import datetime
from email.mime.text import MIMEText

import requests
import streamlit as st

GEMINI_MODELS = ("gemini-3-flash-preview", "gemini-2.5-flash")

SYSTEM_PROMPT = """You are an AI Mental Health Assessment Report Generator.

Your role is to analyze a user's responses to a structured mental health questionnaire and generate a clear, objective, and supportive report. You are NOT a licensed mental health professional and must never diagnose medical or psychiatric conditions. Your purpose is to summarize questionnaire results, identify patterns, and provide educational insights.

Guidelines:

1. Analyze all responses together rather than interpreting individual answers in isolation.

2. Identify possible patterns in the following areas when supported by the responses:
   - Stress
   - Anxiety-related symptoms
   - Mood
   - Depression-related symptoms
   - Sleep quality
   - Emotional regulation
   - Self-esteem
   - Social relationships
   - Burnout
   - Work or academic pressure
   - Lifestyle factors affecting mental well-being

3. Use evidence-based language such as:
   - "The responses suggest..."
   - "The questionnaire indicates..."
   - "There may be signs of..."
   - "The responses are consistent with..."
   Never state or imply a definitive diagnosis.

4. Assign a qualitative severity level for each relevant domain:
   - Minimal
   - Mild
   - Moderate
   - Elevated
   - High

5. Highlight strengths and protective factors when present, including:
   - Healthy coping strategies
   - Good social support
   - Positive routines
   - Resilience
   - Motivation to improve
   - Healthy sleep or exercise habits

6. Identify areas that may benefit from attention.

7. Provide practical, evidence-based recommendations, such as:
   - Sleep hygiene
   - Physical activity
   - Mindfulness
   - Stress management
   - Journaling
   - Time management
   - Social connection
   - Professional counseling if appropriate

8. If responses indicate possible risk of self-harm, suicidal thoughts, or severe psychological distress:
   - Clearly state that the responses indicate a potentially urgent concern.
   - Strongly encourage immediate contact with a licensed mental health professional or local emergency services.
   - Do not attempt to provide therapy.
   - Maintain a calm, supportive, non-judgmental tone.

9. Never:
   - Diagnose disorders.
   - Prescribe medications.
   - Claim certainty.
   - Shame or criticize the user.

10. Write in a compassionate, professional, and easy-to-understand style.

Generate the report using the following structure:

# Mental Health Assessment Report

## Assessment Summary
A concise overview of the overall findings.

## Overall Well-being
Overall assessment of emotional well-being.

## Domain Analysis

For each applicable domain include:
- Severity Level
- Observations
- Supporting evidence from questionnaire responses
- Potential impact

## Strengths and Protective Factors

List positive findings.

## Areas for Improvement

Summarize the primary concerns.

## Personalized Recommendations

Provide actionable recommendations organized by:
- Daily habits
- Stress management
- Sleep
- Physical health
- Social well-being
- Professional support (if appropriate)

## Overall Risk Level

One of:
- Low
- Mild
- Moderate
- Elevated
- High

Provide a brief explanation.

## Important Disclaimer

Include the following disclaimer:

"This report is generated from questionnaire responses and is intended for informational and educational purposes only. It is not a medical diagnosis and should not replace an evaluation by a qualified mental health professional. If you are experiencing severe distress, thoughts of self-harm, or feel unsafe, seek immediate help from a licensed mental health professional or your local emergency services."

Formatting requirements:
- Use clear headings.
- Write in Markdown.
- Keep the report between 700 and 1,200 words.
- Use bullet points where appropriate.
- Avoid technical jargon whenever possible.
- Ensure the report is suitable for inclusion directly in the body of an email."""


def get_secret(name: str):
    try:
        return st.secrets[name]
    except (KeyError, FileNotFoundError):
        return None

st.set_page_config(page_title="Mental Health Check-In", page_icon="🧠", layout="centered")

st.title("🧠 Mental Health Check-In")
st.caption(
    "Answer the questions below honestly. A summary of your responses will be "
    "generated and emailed to you. This is a self-reflection tool, not a medical diagnosis."
)

with st.form("checkin_form"):
    st.subheader("👤 About You")
    name = st.text_input("Your Name")
    email = st.text_input("Your Email (the summary will be sent here)")
    age_group = st.selectbox(
        "Age Group",
        ["Under 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
    )
    occupation = st.selectbox(
        "Occupation",
        ["Student", "Employed (Full-time)", "Employed (Part-time)",
         "Self-employed", "Homemaker", "Unemployed", "Retired", "Other"],
    )

    st.subheader("😊 Mood & Emotions")
    mood = st.selectbox(
        "How would you describe your overall mood in the past 2 weeks?",
        ["Very Happy", "Mostly Happy", "Neutral", "Often Sad", "Very Low / Depressed"],
    )
    anxiety_frequency = st.selectbox(
        "How often have you felt anxious, nervous, or on edge recently?",
        ["Never", "Rarely", "Sometimes", "Often", "Almost Every Day"],
    )
    stress_level = st.slider(
        "Rate your current stress level (1 = No stress, 10 = Extremely stressed)",
        min_value=1, max_value=10, value=5,
    )
    happiness_rating = st.slider(
        "Rate your overall happiness (1 = Very unhappy, 10 = Very happy)",
        min_value=1, max_value=10, value=5,
    )

    st.subheader("😴 Sleep & Energy")
    sleep_hours = st.selectbox(
        "On average, how many hours do you sleep per night?",
        ["Less than 4 hours", "4-6 hours", "6-8 hours", "8-10 hours", "More than 10 hours"],
    )
    sleep_quality = st.slider(
        "Rate your sleep quality (1 = Very poor, 10 = Excellent)",
        min_value=1, max_value=10, value=5,
    )
    energy_level = st.slider(
        "Rate your daily energy level (1 = Always exhausted, 10 = Full of energy)",
        min_value=1, max_value=10, value=5,
    )

    st.subheader("🤝 Social & Lifestyle")
    social_connection = st.selectbox(
        "How connected do you feel to friends and family?",
        ["Very Connected", "Somewhat Connected", "Neutral", "Somewhat Isolated", "Very Isolated"],
    )
    physical_activity = st.selectbox(
        "How often do you exercise or do physical activity?",
        ["Daily", "3-5 times a week", "1-2 times a week", "Rarely", "Never"],
    )
    appetite = st.selectbox(
        "How has your appetite been lately?",
        ["Normal", "Increased", "Decreased", "Very Irregular"],
    )

    st.subheader("🎯 Focus & Coping")
    concentration = st.slider(
        "Rate your ability to focus and concentrate (1 = Very poor, 10 = Excellent)",
        min_value=1, max_value=10, value=5,
    )
    overwhelmed_frequency = st.selectbox(
        "How often do you feel overwhelmed by daily responsibilities?",
        ["Never", "Rarely", "Sometimes", "Often", "Always"],
    )
    coping = st.selectbox(
        "When stressed, how do you usually cope?",
        ["Talking to friends/family", "Exercise or hobbies", "Meditation/Relaxation",
         "Sleeping", "Eating", "Ignoring it / Bottling it up", "Other"],
    )
    support_available = st.selectbox(
        "Do you feel you have someone to talk to when things get hard?",
        ["Yes, always", "Yes, sometimes", "Not really", "No, never"],
    )

    additional_notes = st.text_area(
        "Anything else you'd like to share? (optional)", placeholder="Write here..."
    )

    submitted = st.form_submit_button("Submit Check-In ✅", use_container_width=True)


def compute_score() -> tuple[int, str]:
    """Score out of 100 — higher is better wellbeing."""
    score = 0.0

    # Ratings where higher is better (each out of 10) -> 40 points
    score += (happiness_rating + sleep_quality + energy_level + concentration)  # max 40

    # Stress: lower is better -> 10 points (stress 1 -> 10 pts, stress 10 -> 0 pts)
    score += round((10 - stress_level) * 10 / 9)

    mood_pts = {"Very Happy": 10, "Mostly Happy": 8, "Neutral": 5, "Often Sad": 2, "Very Low / Depressed": 0}
    anxiety_pts = {"Never": 10, "Rarely": 8, "Sometimes": 5, "Often": 2, "Almost Every Day": 0}
    social_pts = {"Very Connected": 10, "Somewhat Connected": 7, "Neutral": 5, "Somewhat Isolated": 2, "Very Isolated": 0}
    overwhelmed_pts = {"Never": 10, "Rarely": 8, "Sometimes": 5, "Often": 2, "Always": 0}
    sleep_pts = {"Less than 4 hours": 0, "4-6 hours": 5, "6-8 hours": 10, "8-10 hours": 8, "More than 10 hours": 4}

    score += mood_pts[mood] + anxiety_pts[anxiety_frequency] + social_pts[social_connection]
    score += overwhelmed_pts[overwhelmed_frequency] + sleep_pts[sleep_hours]

    score = round(score)  # max 100

    if score >= 75:
        category = "Good"
    elif score >= 50:
        category = "Moderate"
    elif score >= 30:
        category = "Needs Attention"
    else:
        category = "Concerning"
    return score, category


def build_summary(score: int, category: str) -> str:
    parts = []
    parts.append(
        f"{name}, aged {age_group} and currently {occupation.lower()}, completed a mental health "
        f"check-in on {datetime.now().strftime('%d %B %Y')}."
    )
    parts.append(
        f"They described their overall mood in the past two weeks as '{mood.lower()}' and reported "
        f"feeling anxious {anxiety_frequency.lower()}, with a self-rated stress level of "
        f"{stress_level}/10 and a happiness rating of {happiness_rating}/10."
    )
    parts.append(
        f"They sleep {sleep_hours.lower()} per night with a sleep quality of {sleep_quality}/10, "
        f"and rated their daily energy at {energy_level}/10."
    )
    parts.append(
        f"Socially, they feel {social_connection.lower()}, exercise {physical_activity.lower()}, "
        f"and their appetite has been {appetite.lower()}."
    )
    parts.append(
        f"Their ability to concentrate is rated {concentration}/10, they feel overwhelmed by daily "
        f"responsibilities {overwhelmed_frequency.lower()}, they usually cope with stress by "
        f"{coping.lower()}, and when asked if they have someone to talk to they said "
        f"'{support_available.lower()}'."
    )
    if additional_notes.strip():
        parts.append(f"Additional notes shared: \"{additional_notes.strip()}\".")
    parts.append(
        f"Overall wellbeing score: {score}/100, which falls in the '{category}' range."
    )
    return " ".join(parts)


def generate_report(summary: str) -> str:
    last_error = None
    for model in GEMINI_MODELS:
        for _ in range(2):
            try:
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    params={"key": get_secret("GEMINI_API_KEY")},
                    json={
                        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                        "contents": [{"role": "user", "parts": [{"text": summary}]}],
                    },
                    timeout=180,
                )
                response.raise_for_status()
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except (requests.exceptions.RequestException, KeyError, IndexError) as exc:
                last_error = exc
    raise RuntimeError("All Gemini models failed") from last_error


def send_report_email(recipient: str, report: str) -> None:
    sender = get_secret("GMAIL_ADDRESS")
    msg = MIMEText(report, "plain", "utf-8")
    msg["Subject"] = "MENTAL HEALTH REPORT"
    msg["From"] = sender
    msg["To"] = recipient
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login(sender, get_secret("GMAIL_APP_PASSWORD"))
        server.send_message(msg)


if submitted:
    if not name.strip() or not email.strip():
        st.error("Please enter your name and email before submitting.")
    elif "@" not in email or "." not in email:
        st.error("Please enter a valid email address.")
    else:
        missing = [k for k in ("GEMINI_API_KEY", "GMAIL_ADDRESS", "GMAIL_APP_PASSWORD") if not get_secret(k)]
        if missing:
            st.error(f"The app is not fully configured yet — missing secrets: {', '.join(missing)}.")
        else:
            score, category = compute_score()
            summary = build_summary(score, category)

            report = None
            with st.spinner("Analyzing your responses..."):
                try:
                    report = generate_report(summary)
                except RuntimeError:
                    st.error("Could not generate your report right now. Please try again later.")

            if report:
                try:
                    send_report_email(email.strip(), report)
                    email_note = f"A copy has been emailed to {email}."
                except (smtplib.SMTPException, OSError):
                    email_note = "The email copy could not be sent, but your full report is below."

                st.success(f"✅ Thank you, {name}! Your check-in has been analyzed. {email_note}")
                st.divider()
                st.markdown(report)
