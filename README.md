<div align="center">

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
<img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>
<img src="https://img.shields.io/badge/NLP-TF--IDF-0B5ED7?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Status-Live-198754?style=for-the-badge"/>

<br/><br/>

# 🏦 RBI Alert Desk

### AI-Powered RBI Circular Intelligence & Compliance Assistant

> *Turning hundreds of dense regulatory circulars into instant, actionable compliance insights — so your team spends time acting, not reading.*

<br/>

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20App-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://rbi-alertdesk.streamlit.app/)
[![GitHub](https://img.shields.io/badge/📁%20Source%20Code-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/athhh07/RBI-AlertDesk)
[![LinkedIn](https://img.shields.io/badge/👤%20Atharva%20Desai-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com)

</div>

---

## 🎯 The Problem

Indian banks and NBFCs receive **400+ RBI circulars every year.**
A compliance team manually triaging every circular risks:

- ⏰ **Missing urgent deadlines** with penalty consequences
- 📋 **Overlooking operational changes** that require process updates
- 💸 **Regulatory penalties** for non-compliance

**RBI Alert Desk solves this** by reading, classifying, and extracting key information from any circular in seconds — automatically.

---

## ✨ What It Does

Paste any RBI circular → get a full compliance brief instantly.

| Feature | Description |
|---|---|
| 🤖 **Auto Classification** | Classifies circular as `INFO`, `OPERATIONAL`, or `URGENT` |
| 📅 **Deadline Extraction** | Pulls explicit deadlines and "within X days" clauses |
| 🗓 **Effective Date** | Detects when the circular comes into force |
| ⚠️ **Penalty Detection** | Distinguishes new penalties from historical references |
| 🏛 **Entity Identification** | Finds which institution types are affected |
| 🔑 **Keyword Extraction** | Tags core regulatory themes (KYC, AML, Fraud, Capital...) |
| ✅ **Compliance Actions** | Lists sentences requiring action from regulated entities |
| 📝 **Auto Summary** | Generates a concise executive summary of the circular |
| ⬇️ **Export Report** | Download full analysis as a `.txt` report |

---

## 🎬 Demo

```
INPUT → Paste RBI Circular Text

────────────────────────────────────────────────────────────
               RBI ALERT DESK — ANALYSIS
────────────────────────────────────────────────────────────

 PREDICTION       URGENT 🚨           Confidence: 91.2%

 📅 DEADLINES     • within 30 days of the date of this circular
                  • on or before March 31, 2026

 🗓 EFFECTIVE     April 01, 2026 (explicit)

 ⚠️  PENALTY      YES — New penalty introduced
                  ₹5,000 per instance of irregularity

 🏛 ENTITIES      • Scheduled Commercial Banks
                  • Urban Co-operative Banks
                  • NBFCs

 🔑 KEYWORDS      Capital · Compliance · Fraud · KYC · Risk

 📝 SUMMARY       The circular introduces a mandatory penalty scheme
                  for bank branches deficient in customer service...
────────────────────────────────────────────────────────────
```

🔗 **Try it live → [rbi-alertdesk.streamlit.app](https://rbi-alertdesk.streamlit.app/)**

---

## 📊 Dataset

| Property | Detail |
|---|---|
| **Source** | Reserve Bank of India — rbi.org.in |
| **Scraping Method** | Selenium + BeautifulSoup |
| **Total Circulars Scraped** | 792 |
| **Period Covered** | January 2024 – June 2026 |
| **Labeled Sample** | 237 (stratified by urgency density) |

### Label Distribution

```
OPERATIONAL  ████████████████████████████░░░░░   175  (73.8%)
URGENT       ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░    41  (17.3%)
INFO         ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    21   (8.9%)
```

---

## 🤖 ML Pipeline

```
RBI Website
    │
    ▼ Selenium + BeautifulSoup
Raw HTML / PDF
    │
    ▼ pdfplumber + text cleaning
Cleaned Circular Text
    │
    ▼ TF-IDF Vectorizer (max_features=5000)
Numerical Feature Matrix
    │
    ▼ Random Forest Classifier
INFO / OPERATIONAL / URGENT
    │
    ▼ Rule-based Extractors
Deadlines · Penalties · Entities · Summary
```

---

## 📈 Model Comparison

| Model | Accuracy | Macro F1 |
|---|---|---|
| 🏆 **Random Forest** | **83.33%** | **0.71** |
| Linear SVM | 85.42% | 0.79 |
| Logistic Regression | 83.33% | 0.71 |

**Selected: Random Forest** — chosen for its interpretability, robustness to overfitting on small datasets, and ability to provide per-class probability scores (confidence %) which power the dashboard's confidence display. SVM does not natively support probability calibration without additional wrapping.

### Classification Report — Final Model (Random Forest)

```
                  Precision    Recall    F1-Score    Support

INFO                 0.60       0.75       0.67         4
OPERATIONAL          0.89       0.92       0.90        36
URGENT               0.67       0.50       0.57         8

Accuracy                                   0.83        48
Macro Avg            0.72       0.72       0.71        48
Weighted Avg         0.83       0.83       0.83        48
```

**Reading the results:**
- ✅ **OPERATIONAL (F1: 0.90)** — model learned this class extremely well, makes sense given 175 training examples
- ⚠️ **INFO (F1: 0.67)** — reasonable given only 21 training examples; more labeled data would improve this
- ⚠️ **URGENT (F1: 0.57)** — hardest class: URGENT circulars often use the same "shall/must/comply" language as OPERATIONAL ones, making them genuinely difficult to distinguish without deeper context
- 📌 **Key insight:** weighted avg F1 of 0.83 is strong for a 3-class imbalanced dataset with 237 training examples; a LegalBERT fine-tune is the natural next step to push URGENT recall above 0.70

---

## 🔍 Key EDA Findings

- 📈 **RBI circular volume jumped 4× from 2024 → 2025** (114 → 417 circulars), signalling a major regulatory push.
- 🗓 **April is consistently the busiest month** across all years — likely driven by financial year-end compliance updates.
- 📏 **Document length ranges from 65 to 125,000+ words** — raw urgency keyword counts are unreliable; urgency *density* (per 1,000 words) is a far better signal.
- ⚠️ **"Shall" appears 58,000+ times** across the corpus — almost universal in regulatory language and poor as a standalone urgency signal without normalization.
- 🏦 **"Bank" and "NBFC" dominate entity mentions** — 789 and 182 circulars respectively, confirming the breadth of entities affected.

---

## 📁 Project Structure

```
RBI-AlertDesk/
│
├── 📄 app.py                    ← Streamlit dashboard
├── 📄 extractors.py             ← All extraction functions
├── 📄 requirements.txt
├── 📄 README.md
│
├── 📂 models/
│   ├── rbi_classifier.pkl       ← Trained Random Forest
│   └── tfidf_vectorizer.pkl     ← Trained TF-IDF vectorizer
│
├── 📂 data/
│   ├── raw/                     ← Scraped HTML files
│   ├── processed/               ← Cleaned circular text
│   └── labeled/                 ← 237 manually labeled circulars
│
├── 📂 notebooks/
│   ├── 01_scraping.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_modeling.ipynb
│   ├── 04_labeling.ipynb
│   └── 06_information_extraction.ipynb
│
└── 📂 results/
    └── classification_report.txt
```

---

## 🚀 Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/athhh07/RBI-AlertDesk.git
cd RBI-AlertDesk

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## ☁️ Deployed On

<div align="center">

[![Streamlit Community Cloud](https://img.shields.io/badge/Streamlit%20Community%20Cloud-Deployed-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://rbi-alertdesk.streamlit.app/)

**🔗 Live URL: [https://rbi-alertdesk.streamlit.app/](https://rbi-alertdesk.streamlit.app/)**

</div>

### Deploy Your Own Copy

1. Fork this repository on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your forked repo → set main file as `app.py`
4. Click **Deploy** — live in ~2 minutes

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Web Scraping | Selenium, BeautifulSoup |
| PDF Parsing | pdfplumber |
| ML / NLP | scikit-learn, TF-IDF |
| Dashboard | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Model Storage | Joblib |
| Deployment | Streamlit Community Cloud |

---

## 🔮 Future Improvements

- [ ] 🧠 **LegalBERT / FinBERT** — domain-adapted transformer for higher accuracy
- [ ] 💡 **SHAP Explainability** — show which words drove the prediction
- [ ] 📧 **Email Alerts** — auto-notify teams when URGENT circulars are published
- [ ] 🔎 **Semantic Search** — find similar past circulars using embeddings
- [ ] 📄 **PDF Upload** — drag-and-drop PDF support
- [ ] 🤖 **LLM Integration** — GPT/Claude-powered compliance Q&A on top of circulars

---

## 👨‍💻 Developer

<div align="center">

**Atharva Desai**
B.Tech Computer Science & Engineering (Data Science)

[![GitHub](https://img.shields.io/badge/GitHub-athhh07-181717?style=flat-square&logo=github)](https://github.com/athhh07)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com)

*Built as a portfolio project demonstrating end-to-end ML + NLP pipeline development on real Indian regulatory data.*

</div>

---

## 📄 License

This project is developed for educational and portfolio purposes.
Data sourced from the public domain at [rbi.org.in](https://www.rbi.org.in).

---

<div align="center">
  <sub>⭐ Star this repo if you found it useful</sub>
</div>
