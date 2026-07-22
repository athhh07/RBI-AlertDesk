# 🏦 RBI Alert Desk

**AI-Powered RBI Circular Intelligence & Compliance Assistant**

Automatically classifies RBI circulars as INFO / OPERATIONAL / URGENT and extracts deadlines,
penalties, affected entities, keywords, compliance actions, and a summary.

---

## Folder Structure

```
rbi-alert-desk/
├── app.py                  ← Main Streamlit application
├── extractors.py           ← All extraction functions
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
└── models/
    ├── rbi_classifier.pkl  ← Trained Random Forest model
    └── tfidf_vectorizer.pkl← Trained TF-IDF vectorizer
```

---

## Run Locally

```bash
# 1. Clone or download the project folder
cd rbi-alert-desk

# 2. Install dependencies
pip install -r requirements.txt

# 3. Make sure your model files are in the models/ folder

# 4. Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## Deploy to Hugging Face Spaces

### Step 1 — Create a new Space
1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Enter a name: `rbi-alert-desk`
4. Select **SDK: Streamlit**
5. Choose visibility: **Public**
6. Click **Create Space**

### Step 2 — Upload your files
Upload ALL of these into the Space:
```
app.py
extractors.py
requirements.txt
models/rbi_classifier.pkl
models/tfidf_vectorizer.pkl
```

You can upload via the web UI (drag and drop) or use Git:

```bash
# Using Git
git clone https://huggingface.co/spaces/YOUR_USERNAME/rbi-alert-desk
cd rbi-alert-desk

# Copy your files in
cp /path/to/your/app.py .
cp /path/to/your/extractors.py .
cp /path/to/your/requirements.txt .
mkdir models
cp /path/to/your/models/*.pkl models/

# Push
git add .
git commit -m "Initial deployment"
git push
```

### Step 3 — Wait for build
Hugging Face will automatically install dependencies and start the app.
Build takes 2-5 minutes on first deploy.

### Step 4 — Share your Space URL
Your app will be live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/rbi-alert-desk
```

---

## Important Notes

- **Model files are large** — if your `.pkl` files are over 100MB, use
  [Git LFS](https://huggingface.co/docs/hub/repositories-getting-started#terminal)
  to upload them.
- **extractors.py must be in the root folder** — same level as app.py,
  not inside a subfolder.
- The app loads the model once and caches it (`@st.cache_resource`),
  so subsequent analyses are fast.

---

## Tech Stack

| Component   | Technology              |
|-------------|------------------------|
| Frontend    | Streamlit              |
| Classifier  | Random Forest (sklearn)|
| Vectorizer  | TF-IDF (sklearn)       |
| Data        | 237 RBI Circulars      |
| Coverage    | 2024 – 2026            |
| Developer   | Atharva Desai          |
