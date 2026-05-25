# 🧠 MindTrace — Health Sentiment Tracker

> **Write how you're feeling. AI tracks your emotional health — privately, locally, instantly.**

MindTrace is an open-source NLP-powered journaling application that analyses every entry you write, classifies your emotion, scores your sentiment, and visualises your mood trends over time. Zero cloud dependencies. Zero subscriptions. All data stays on your machine.

---

## 📋 Table of Contents

- [Project Overview & Motivation](#-project-overview--motivation)
- [Tech Stack](#-tech-stack)
- [Setup Instructions](#-setup-instructions)
- [How to Use the Journaling Interface](#-how-to-use-the-journaling-interface)
- [Sample Visualisations](#-sample-visualisations)
- [Ethical Considerations](#-ethical-considerations)

---

## 🌟 Project Overview & Motivation

Mental health journaling is a clinically backed practice — but most digital tools are either dumb text boxes or locked behind cloud services that process your private thoughts on remote servers. MindTrace takes a different approach:

- **Local-first**: Your journal entries never leave your machine.
- **Instant analysis**: NLTK VADER scores sentiment in under 10ms.
- **Health-aware**: Emotion keywords include clinical language like `pain`, `fatigue`, `nausea`, `chronic symptoms`.
- **Trend-aware**: Charts let you see patterns across days or weeks, not just a single entry.

The app was built to answer a simple question: *Can a two-file Python project meaningfully track emotional health without any API keys, cloud calls, or heavy frameworks?* The answer is yes.

### What It Does

| Feature | Description |
|---|---|
| 📝 Journal | Write free-text entries; receive instant emotion + wellness analysis |
| 🎭 Emotion Classification | 9 categories: hopeful, calm, grateful, anxious, tired, sad, angry, pain, neutral |
| 📊 Sentiment Score | VADER compound score from −1.0 (very negative) to +1.0 (very positive) |
| 💊 Wellness Score | 1–10 integer derived from sentiment + emotion type modifiers |
| 📈 Trends Chart | Sentiment and wellness plotted over your last 50 entries |
| 🎭 Distribution | Bar chart of emotion frequency across all entries |
| 💡 Insights | Auto-generated health observations from your patterns |
| 🏷️ Keywords | Top 6 content words extracted from each entry |

---

## 🛠 Tech Stack

### Backend
| Technology | Version | Role |
|---|---|---|
| **Python** | 3.8+ | Runtime |
| **Flask** | ≥3.0 | Web framework + REST API |
| **NLTK VADER** | ≥3.8 | Sentiment analysis engine |
| **SQLite3** | stdlib | Embedded zero-config database |

### Frontend
| Technology | Source | Role |
|---|---|---|
| **HTML5 / CSS3** | Inline | Full dark-mode UI, design token system |
| **Vanilla JavaScript** | Inline | API calls, DOM updates, view routing |
| **Plotly.js** | CDN v2.27.0 | Interactive charts |

### Why These Choices?
- **Flask** — minimal surface area; no boilerplate, ships with a dev server.
- **NLTK VADER** — no model downloads, no GPU, no API key. Runs from a 1.6 MB lexicon file.
- **SQLite** — zero setup, serverless, perfect for single-user local applications.
- **Vanilla JS + Plotly** — no build step, no npm, no bundler. Open the file and it works.

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.8 or newer
- pip
- A modern browser (Chrome, Firefox, Safari, Edge)
- ~15 MB disk space for NLTK corpora (one-time download)

### 1 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs `flask>=3.0` and `nltk>=3.8`. Nothing else.

> **Tip:** Use a virtual environment to keep things tidy:
> ```bash
> python3 -m venv venv && source venv/bin/activate   # macOS/Linux
> venv\Scripts\activate                               # Windows
> pip install -r requirements.txt
> ```

### 2 — Download NLTK Corpora (one-time)

```bash
python3 -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
```

> **Note:** The app also attempts this automatically on startup, so this step is optional if you have an internet connection.

### 3 — Run the Application

```bash
python3 app.py
```

You'll see:

```
✅  MindTrace running → http://127.0.0.1:5000
```

Open that URL in your browser. The `journal.db` SQLite database is created automatically on first run.

### Troubleshooting

| Issue | Fix |
|---|---|
| `Port 5000 already in use` | Change `port=5000` on the last line of `app.py` |
| `NLTK LookupError` | Run the Step 2 command manually |
| `ModuleNotFoundError: flask` | Re-run `pip install -r requirements.txt` |
| `TemplateNotFound: index.html` | Make sure you `cd mindtrace/` before running the app |

---

## 📓 How to Use the Journaling Interface

### Writing an Entry

1. The app opens on the **Journal** tab. You'll see a large text area with the placeholder *"How are you feeling today? Describe your mood, symptoms, energy levels, thoughts..."*
2. Type freely — there's no required format. Write a sentence or several paragraphs.
3. Optionally click a **Quick Tag** (anxious, hopeful, tired, in pain, calm, overwhelmed, grateful, frustrated, sad, motivated) to append that word to your entry.
4. Click **Analyze & Save**.

### Reading Your Results

After saving, a result card appears below the text area showing:

- **Emotion badge** — a coloured pill with an emoji and emotion label
- **Sentiment score** — the raw VADER compound value (e.g. `+0.34`)
- **Wellness score** — a 1–10 integer (e.g. `Wellness: 7/10`)
- **Keywords** — the most prominent content words from your entry

### Navigating Between Views

Use the left sidebar to switch views:

| View | What You'll See |
|---|---|
| **📝 Journal** | The entry composer + recent entries in the sidebar |
| **📈 Trends** | Two Plotly charts: sentiment over time + emotion distribution |
| **💡 Insights** | Auto-generated observations based on your entry patterns |

### Managing Entries

- Hover any entry in the sidebar to reveal a **delete button** (×).
- The top stat bar always shows: Total Entries, Avg Sentiment, Dominant Mood, Avg Wellness.

### API Access

For power users and developers, MindTrace exposes a clean REST API:

```
POST   /api/analyze          — Analyse and save a new entry
GET    /api/entries?limit=N  — Retrieve recent entries (default 30)
GET    /api/stats            — Aggregated statistics
DELETE /api/delete/<id>      — Remove an entry by ID
```

---

## 📊 Sample Visualisations

MindTrace renders two Plotly.js charts on the **Trends** tab:

### Sentiment Over Time
A dual-trace line chart showing:
- **Blue line** — raw VADER compound score per entry (−1.0 to +1.0)
- **Teal bars** — normalised wellness contribution

The x-axis is the entry timestamp; the y-axis ranges from −1.0 to +1.0. A horizontal zero line makes positive/negative periods immediately visible.

```
+1.0 ┤         ╭──╮
     │    ╭────╯  │
 0.0 ┼────╯       ╰──────╮
     │                   ╰────
-1.0 ┘
     Mon  Tue  Wed  Thu  Fri  Sat
```

### Emotion Distribution
A vertical bar chart where each bar represents one of the 9 emotion categories. The height encodes how many times that emotion appeared across all saved entries. Bars are colour-coded by valence (green = positive, red = negative, grey = neutral).

**Example distribution after 11 entries:**
```
hopeful  ████████  4
calm     ████      2
anxious  ████      2
tired    ██        1
pain     ██        1
sad      █         1
```

### Insights Panel
Client-side rule engine generates contextual observations such as:

- 📈 *Improving mood trend* — recent entries more positive than earlier ones
- 📉 *Declining mood detected* — consider speaking with a healthcare provider
- 😴 *Fatigue pattern noticed* — multiple recent entries flagged as tired
- 🧘 *Most entries are calm or hopeful* — emotional stability observed
- 🏷️ *Top themes* — keyword summary across recent entries

---

## ⚠️ Ethical Considerations

> **MindTrace is a personal wellness journaling aid. It is NOT a clinical diagnostic tool, medical device, or substitute for professional mental health care.**

### Clinical Limitations
- **VADER** was trained on social-media text, not clinical language. Compound scores are approximations, not validated psychometric measurements (e.g. PHQ-9, GAD-7).
- **Keyword matching** is a heuristic. Sarcasm, metaphor, or culturally specific language may be misclassified.
- **The wellness score** (1–10) is a composite heuristic. Do not use it for clinical decision-making.
- If the Insights panel flags a declining mood pattern, treat this as a prompt to seek professional support — not as a diagnosis.

### Data & Privacy
- All journal data is stored **exclusively on your local machine** in `journal.db`.
- No data is transmitted to any external server or API.
- The default configuration has **no authentication**. Do not deploy MindTrace on a public or shared server without adding appropriate access controls.
- MindTrace is not HIPAA or GDPR compliant out of the box. Clinical or organisational deployment requires independent legal assessment.

### Transparency
- Emotion labels and insights are generated by **automated rules and statistical models**, not human clinicians.
- Users should understand that phrases like "Declining mood detected" are algorithmic observations, not medical opinions.

### Responsible Use Matrix

| Use Case | Appropriate? |
|---|---|
| Personal daily mood journaling | ✅ Yes — primary use case |
| Sharing trends with a therapist as context | ✅ Yes, with consent |
| Informal chronic-illness symptom tracking | ✅ Yes, with awareness of limitations |
| Replacing clinical mental health assessments | ❌ No |
| Multi-user clinic or workplace deployment | ⚠️ Requires auth, encryption, legal review |
| Academic research data collection | ⚠️ Requires IRB approval and informed consent |

---

## 📁 Project Structure

```
mindtrace/
├── app.py              # Flask server + NLP logic + API routes (~140 lines)
├── requirements.txt    # flask>=3.0  nltk>=3.8
├── journal_backup.db          # SQLite database (auto-created on first run)
├── templates/
│   └── index.html      # Complete SPA: HTML + CSS + JS (~750 lines)
└── README.md
```

---

*MindTrace — track your mind, understand your patterns, respect your privacy.*
