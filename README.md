# Mental Health Check-In (Streamlit + n8n)

A Streamlit form that collects mental health check-in answers (dropdowns + rating sliders),
computes a wellbeing score, builds a summary paragraph, and POSTs everything as JSON to an
n8n webhook so n8n can email the summary to the user.

## Run

```
pip install -r requirements.txt
streamlit run app.py
```

Make sure n8n is running locally and the workflow with this webhook is **active**
(or click "Listen for test event" and use the test URL while building):

```
http://localhost:5678/webhook/a1bc4ec1-5434-4740-a439-2c91919b865e
```

## JSON payload sent to n8n

Flat JSON (easy to reference in n8n as `{{ $json.body.field }}`):

| Field | Type | Example |
|---|---|---|
| name | string | "Dhruv" |
| email | string | "user@example.com" |
| age_group | string | "18-24" |
| occupation | string | "Student" |
| mood | string | "Neutral" |
| anxiety_frequency | string | "Sometimes" |
| stress_level | number | 6 |
| happiness_rating | number | 7 |
| sleep_hours | string | "6-8 hours" |
| sleep_quality | number | 6 |
| energy_level | number | 5 |
| social_connection | string | "Somewhat Connected" |
| physical_activity | string | "1-2 times a week" |
| appetite | string | "Normal" |
| concentration | number | 6 |
| overwhelmed_frequency | string | "Sometimes" |
| coping | string | "Exercise or hobbies" |
| support_available | string | "Yes, sometimes" |
| additional_notes | string | "" |
| wellbeing_score | number | 68 |
| wellbeing_category | string | "Moderate" |
| summary | string | full paragraph summary |
| submitted_at | string (ISO) | "2026-07-24T10:30:00+00:00" |

## Suggested n8n workflow

1. **Webhook** node — method: POST, path: `a1bc4ec1-5434-4740-a439-2c91919b865e`.
2. *(Optional)* **AI / LLM** node — refine `{{ $json.body.summary }}` into a friendlier email.
3. **Send Email / Gmail** node —
   - To: `{{ $json.body.email }}`
   - Subject: `Your Mental Health Check-In Summary ({{ $json.body.wellbeing_category }})`
   - Body: use `{{ $json.body.summary }}` and `{{ $json.body.wellbeing_score }}`.

Note: with the default Webhook node settings, the POSTed fields are under `body`
(`$json.body.name` etc.). If you enabled "Raw body" or changed options, adjust accordingly.
