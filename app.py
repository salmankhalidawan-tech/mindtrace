from flask import Flask, render_template, request, jsonify
import sqlite3, json, re
from datetime import datetime, timedelta
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import nltk

app = Flask(__name__)
DB = "journal.db"

# ── NLTK setup ──────────────────────────────────────────────
for res in ["vader_lexicon", "punkt", "punkt_tab", "stopwords"]:
    try:
        nltk.download(res, quiet=True)
    except Exception as e:
        print(f"Warning: could not download NLTK resource {res}: {e}")

sia = SentimentIntensityAnalyzer()
STOP = set(stopwords.words("english"))

EMOTION_KEYWORDS = {
    "anxious":  ["anxious","anxiety","worried","nervous","panic","stress","stressed","tense","uneasy","dread","fear","scared","restless"],
    "hopeful":  ["hope","hopeful","optimistic","excited","looking forward","better","improve","positive","motivated","inspired","confident"],
    "sad":      ["sad","unhappy","cry","crying","depressed","depression","empty","lonely","grief","heartbroken","miserable","down"],
    "angry":    ["angry","anger","furious","frustrated","rage","annoyed","irritated","mad","upset","resentful"],
    "calm":     ["calm","relaxed","peaceful","serene","content","tranquil","comfortable","at ease","settled","mindful"],
    "tired":    ["tired","exhausted","fatigued","drained","sleepy","weary","burnout","lethargic","weak","no energy"],
    "grateful": ["grateful","thankful","blessed","appreciate","appreciation","gratitude","fortunate","lucky"],
    "pain":     ["pain","aching","hurt","sore","discomfort","chronic","symptoms","headache","nausea","fatigue","illness"],
}

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                text      TEXT NOT NULL,
                emotion   TEXT,
                sentiment REAL,
                wellness  INTEGER,
                created   TEXT DEFAULT (datetime('now','localtime'))
            )
        """)
        db.commit()

# ── Sentiment analysis ───────────────────────────────────────
def classify_emotion(text, scores):
    lower = text.lower()
    hits = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        count = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', lower))
        if count:
            hits[emotion] = count

    compound = scores["compound"]
    if hits:
        primary = max(hits, key=hits.get)
        return primary

    if compound >= 0.35:  return "hopeful"
    if compound >= 0.05:  return "calm"
    if compound <= -0.5:  return "sad"
    if compound <= -0.2:  return "anxious"
    return "neutral"

def get_wellness(compound, emotion):
    base = int((compound + 1) / 2 * 7) + 2   # 2-9
    boosts = {"hopeful": 1, "grateful": 1, "calm": 0}
    drops  = {"sad": -2, "angry": -1, "pain": -1, "tired": -1, "anxious": -1}
    return max(1, min(10, base + boosts.get(emotion, 0) + drops.get(emotion, 0)))

def get_top_words(text):
    tokens = word_tokenize(text.lower())
    words  = [w for w in tokens if w.isalpha() and w not in STOP and len(w) > 3]
    return [w for w, _ in Counter(words).most_common(6)]

def analyze(text):
    scores  = sia.polarity_scores(text)
    emotion = classify_emotion(text, scores)
    wellness = get_wellness(scores["compound"], emotion)
    keywords = get_top_words(text)
    return {
        "compound": round(scores["compound"], 3),
        "pos":      round(scores["pos"], 2),
        "neg":      round(scores["neg"], 2),
        "neu":      round(scores["neu"], 2),
        "emotion":  emotion,
        "wellness": wellness,
        "keywords": keywords,
    }

# ── Routes ───────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Invalid request format"}), 400
    text = data.get("text", "").strip()
    if len(text) < 5:
        return jsonify({"error": "Too short"}), 400
    result = analyze(text)
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO entries (text,emotion,sentiment,wellness) VALUES (?,?,?,?)",
            (text, result["emotion"], result["compound"], result["wellness"])
        )
        db.commit()
        result["id"] = cur.lastrowid
    return jsonify(result)

@app.route("/api/entries")
def api_entries():
    try:
        limit = int(request.args.get("limit", 30))
    except ValueError:
        limit = 30
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM entries ORDER BY created DESC LIMIT ?", (limit,)
        ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/delete/<int:entry_id>", methods=["DELETE"])
def api_delete(entry_id):
    with get_db() as db:
        db.execute("DELETE FROM entries WHERE id=?", (entry_id,))
        db.commit()
    return jsonify({"ok": True})

@app.route("/api/stats")
def api_stats():
    with get_db() as db:
        rows = db.execute("SELECT emotion, sentiment, wellness, created FROM entries").fetchall()
    if not rows:
        return jsonify({"total":0})

    total    = len(rows)
    avg_sent = round(sum(r["sentiment"] for r in rows) / total, 3)
    avg_well = round(sum(r["wellness"]  for r in rows) / total, 1)
    emotions = Counter(r["emotion"] for r in rows)
    dominant = emotions.most_common(1)[0][0]

    # Last 14 days trend
    cutoff = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    recent = [r for r in rows if r["created"][:10] >= cutoff]
    trend_dates  = [r["created"][:10] for r in recent]
    trend_scores = [r["sentiment"]     for r in recent]

    return jsonify({
        "total":    total,
        "avg_sent": avg_sent,
        "avg_well": avg_well,
        "dominant": dominant,
        "emotions": dict(emotions),
        "trend_dates":  trend_dates,
        "trend_scores": trend_scores,
    })

if __name__ == "__main__":
    init_db()
    print("\n✅  MindTrace running → http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
