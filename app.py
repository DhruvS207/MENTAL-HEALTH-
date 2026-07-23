import json
from datetime import datetime, timezone

import requests
import streamlit as st

WEBHOOK_URL = "http://localhost:5678/webhook/a1bc4ec1-5434-4740-a439-2c91919b865e"

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


if submitted:
    if not name.strip() or not email.strip():
        st.error("Please enter your name and email before submitting.")
    elif "@" not in email or "." not in email:
        st.error("Please enter a valid email address.")
    else:
        score, category = compute_score()
        summary = build_summary(score, category)

        payload = {
            "name": name.strip(),
            "email": email.strip(),
            "age_group": age_group,
            "occupation": occupation,
            "mood": mood,
            "anxiety_frequency": anxiety_frequency,
            "stress_level": stress_level,
            "happiness_rating": happiness_rating,
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "energy_level": energy_level,
            "social_connection": social_connection,
            "physical_activity": physical_activity,
            "appetite": appetite,
            "concentration": concentration,
            "overwhelmed_frequency": overwhelmed_frequency,
            "coping": coping,
            "support_available": support_available,
            "additional_notes": additional_notes.strip(),
            "wellbeing_score": score,
            "wellbeing_category": category,
            "summary": summary,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            response = requests.post(
                WEBHOOK_URL,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            if response.ok:
                st.success(f"✅ Thank you, {name}! Your check-in has been submitted. A summary email will be delivered to {email}.")
            else:
                st.error("Something went wrong while submitting. Please try again later.")
        except requests.exceptions.RequestException:
            st.error("Could not submit your check-in right now. Please try again later.")
