"""
RBI Alert Desk — AI-Powered RBI Circular Intelligence & Compliance Assistant
"""

import re
import joblib
import fitz
import streamlit as st
from datetime import datetime

from extractors import (
    extract_deadline,
    extract_effective_date,
    detect_penalty,
    extract_entities,
    extract_keywords,
    extract_actions,
    generate_summary,
)


# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="RBI Alert Desk",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --blue: #0B5ED7;
    --navy: #0F172A;
    --green: #198754;
    --amber: #F59E0B;
    --red: #DC3545;
    --bg: #F8FAFC;
    --surface: #FFFFFF;
    --border: #E2E8F0;
    --text-1: #0F172A;
    --text-2: #475569;
    --text-3: #94A3B8;
    --radius: 12px;
    --shadow: 0 1px 3px rgba(0,0,0,.08),
               0 4px 16px rgba(0,0,0,.06);
    --shadow-md: 0 4px 6px rgba(0,0,0,.07),
                 0 10px 24px rgba(0,0,0,.10);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
}

#MainMenu,
footer,
header {
    visibility: hidden;
}

[data-testid="stSidebar"] > div:first-child {
    background: var(--navy) !important;
}

[data-testid="stSidebar"] * {
    color: #CBD5E1 !important;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F1F5F9 !important;
}


/* ── Pulse bar ── */

.pulse-bar {
    width: 100%;
    height: 5px;
    border-radius: 99px;
    margin-bottom: 2rem;
    background: linear-gradient(
        90deg,
        var(--blue) 0%,
        #60A5FA 100%
    );
    animation: pulse-grow 1.2s ease-out forwards;
    transform-origin: left;
}

.pulse-bar.urgent {
    background: linear-gradient(
        90deg,
        var(--red) 0%,
        #FCA5A5 100%
    );
}

.pulse-bar.operational {
    background: linear-gradient(
        90deg,
        var(--amber) 0%,
        #FDE68A 100%
    );
}

.pulse-bar.info {
    background: linear-gradient(
        90deg,
        var(--green) 0%,
        #6EE7B7 100%
    );
}

@keyframes pulse-grow {
    from {
        transform: scaleX(0);
    }

    to {
        transform: scaleX(1);
    }
}


/* ── Hero ── */

.hero {
    background: linear-gradient(
        135deg,
        var(--navy) 0%,
        #1E3A5F 100%
    );
    border-radius: var(--radius);
    padding: 2.5rem 2rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}

.hero::after {
    content: '';
    position: absolute;
    top: -60px;
    right: -60px;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: rgba(11,94,215,.25);
    pointer-events: none;
}

.hero-title {
    font-size: 2rem;
    font-weight: 700;
    color: #F1F5F9;
    margin: 0 0 .4rem;
    letter-spacing: -.5px;
}

.hero-sub {
    font-size: .95rem;
    color: #94A3B8;
    max-width: 650px;
    line-height: 1.6;
}

.hero-badge {
    display: inline-block;
    background: rgba(11,94,215,.35);
    color: #93C5FD;
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    padding: .25rem .7rem;
    border-radius: 99px;
    margin-bottom: .8rem;
    border: 1px solid rgba(147,197,253,.25);
}


/* ── Cards ── */

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}

.card:hover {
    box-shadow: var(--shadow-md);
}

.card-label {
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: .5rem;
}

.card-value {
    font-size: .95rem;
    font-weight: 500;
    color: var(--text-1);
    line-height: 1.55;
}


/* ── Prediction badge ── */

.pred-badge {
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    font-size: 1.5rem;
    font-weight: 700;
    padding: .6rem 1.6rem;
    border-radius: 99px;
    letter-spacing: .03em;
}

.pred-urgent {
    background: #FEF2F2;
    color: var(--red);
    border: 2px solid #FECACA;
}

.pred-operational {
    background: #FFFBEB;
    color: #B45309;
    border: 2px solid #FDE68A;
}

.pred-info {
    background: #F0FDF4;
    color: var(--green);
    border: 2px solid #BBF7D0;
}


/* ── Metric tiles ── */

.metric-tile {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow);
    text-align: center;
}

.metric-icon {
    font-size: 1.6rem;
}

.metric-label {
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--text-3);
    margin: .3rem 0 .1rem;
}

.metric-val {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-1);
}


/* ── Tags ── */

.tag-row {
    display: flex;
    flex-wrap: wrap;
    gap: .4rem;
    margin-top: .2rem;
}

.tag {
    display: inline-block;
    background: #EFF6FF;
    color: var(--blue);
    font-size: .75rem;
    font-weight: 500;
    padding: .2rem .65rem;
    border-radius: 99px;
    border: 1px solid #BFDBFE;
    font-family: 'JetBrains Mono', monospace;
}

.tag-entity {
    background: #F0FDF4;
    color: #166534;
    border-color: #BBF7D0;
}


/* ── Section header ── */

.section-header {
    font-size: .8rem;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--text-3);
    border-bottom: 1px solid var(--border);
    padding-bottom: .5rem;
    margin: 1.5rem 0 1rem;
}


/* ── Textarea ── */

textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: .9rem !important;
}


/* ── Actions ── */

.action-item {
    border-left: 3px solid var(--blue);
    padding: .45rem .8rem;
    margin-bottom: .5rem;
    background: #F8FAFC;
    border-radius: 0 6px 6px 0;
    font-size: .85rem;
    line-height: 1.5;
    color: var(--text-1);
}


/* ── Deadline ── */

.deadline-item {
    display: flex;
    align-items: flex-start;
    gap: .5rem;
    padding: .5rem .7rem;
    margin-bottom: .4rem;
    background: #FEF2F2;
    border-radius: 8px;
    border-left: 3px solid var(--red);
    font-size: .85rem;
    color: #7F1D1D;
    font-family: 'JetBrains Mono', monospace;
}


/* ── Buttons ── */

.stDownloadButton > button {
    background: var(--navy) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: .83rem !important;
    padding: .45rem 1rem !important;
}

.stDownloadButton > button:hover {
    background: var(--blue) !important;
}

.stButton > button {
    background: var(--blue) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: .9rem !important;
    padding: .55rem 1.6rem !important;
}


/* ── Sidebar links ── */

.nav-link {
    display: block;
    padding: .4rem .6rem;
    border-radius: 6px;
    color: #94A3B8 !important;
    font-size: .85rem;
    text-decoration: none;
}

.nav-link:hover {
    background: rgba(255,255,255,.08);
    color: #F1F5F9 !important;
}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MODEL LOADING
# ─────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_model():

    model = joblib.load(
        "models/rbi_classifier.pkl"
    )

    tfidf = joblib.load(
        "models/tfidf_vectorizer.pkl"
    )

    return model, tfidf


# ─────────────────────────────────────────────────────────────
# PDF TEXT EXTRACTION
# ─────────────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file):

    pdf_bytes = uploaded_file.read()

    doc = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    pages_text = []

    for page in doc:

        page_text = page.get_text()

        if page_text:
            pages_text.append(page_text)

    doc.close()

    return "\n".join(
        pages_text
    ).strip()


# ─────────────────────────────────────────────────────────────
# CLEAN EFFECTIVE DATE
# ─────────────────────────────────────────────────────────────

def clean_effective_date(effective):

    if isinstance(effective, dict):

        effective = effective.get(
            "effective_date",
            ""
        )

    if not effective:

        return "Not specified"

    effective = str(
        effective
    ).strip()


    # Try to extract an actual date from phrases such as:
    # "shall come into effect on January 01, 2027"

    date_pattern = re.compile(
        r"""
        \b
        (
            January|February|March|April|May|June|
            July|August|September|October|November|December
        )
        \s+
        (\d{1,2})
        (?:st|nd|rd|th)?
        (?:,)?\s+
        (\d{4})
        \b
        """,
        re.IGNORECASE |
        re.VERBOSE
    )


    match = date_pattern.search(
        effective
    )


    if match:

        month = match.group(1)

        day = match.group(2)

        year = match.group(3)

        return f"{month} {day}, {year}"


    return effective


# ─────────────────────────────────────────────────────────────
# ENTITY CLEANING
# ─────────────────────────────────────────────────────────────

def clean_entities(
    entities,
    circular_text=""
):

    cleaned = []


    # Action phrases that should NEVER appear
    # in Affected Entities.

    bad_starts = (
        "be ",
        "shall ",
        "will ",
        "should ",
        "must ",
        "may ",
        "to be ",
        "is to ",
        "are to ",
    )


    action_words = {

        "amended",
        "amend",
        "called",
        "consolidated",
        "ensured",
        "ensure",
        "disclosed",
        "disclose",
        "inserted",
        "insert",
        "listed",
        "displayed",
        "reported",
        "maintained",
        "submitted",
        "implemented",
        "followed",
        "complied",
        "applicable",
        "prescribed",
        "required",
    }


    for entity in entities or []:

        if entity is None:
            continue


        entity = str(
            entity
        ).strip()


        if not entity:
            continue


        entity_lower = entity.lower()


        # Remove phrases starting with actions.

        if entity_lower.startswith(
            bad_starts
        ):
            continue


        # Remove action-only words.

        words = entity_lower.split()

        if words and words[0] in action_words:
            continue


        # Remove long sentence fragments.

        if len(entity.split()) > 7:
            continue


        # Remove phrases containing obvious actions.

        bad_patterns = [

            "be amended",
            "be called",
            "be consolidated",
            "be ensured",
            "be disclosed",
            "be inserted",
            "be listed",
            "be displayed",
            "be reported",
            "be maintained",
            "be submitted",
            "be implemented",
            "be followed",
            "be complied",

        ]


        if any(
            pattern in entity_lower
            for pattern in bad_patterns
        ):
            continue


        if entity not in cleaned:

            cleaned.append(
                entity
            )


    # ─────────────────────────────────────────────────────────
    # Detect common RBI-regulated entity types directly
    # from the circular text.
    #
    # This helps when the original extractor captures
    # sentence fragments instead of the actual entity.
    # ─────────────────────────────────────────────────────────

    entity_patterns = {

        "Commercial Banks": [
            r"\bcommercial banks?\b",
            r"\bscheduled commercial banks?\b",
        ],

        "Regional Rural Banks": [
            r"\bregional rural banks?\b",
            r"\brrbs?\b",
        ],

        "Co-operative Banks": [
            r"\bco[- ]operative banks?\b",
            r"\bcooperative banks?\b",
        ],

        "Small Finance Banks": [
            r"\bsmall finance banks?\b",
        ],

        "Payments Banks": [
            r"\bpayments banks?\b",
            r"\bpayment banks?\b",
        ],

        "NBFCs": [
            r"\bnon[- ]banking financial companies\b",
            r"\bnon[- ]banking financial company\b",
            r"\bnbfcs?\b",
        ],

        "Insurance Companies": [
            r"\binsurance companies\b",
            r"\binsurance company\b",
        ],

        "Mutual Funds": [
            r"\bmutual funds?\b",
        ],

        "Pension Funds": [
            r"\bpension funds?\b",
        ],

        "Customers": [
            r"\bcustomers?\b",
        ],

        "Banks": [
            r"\bbanks?\b",
        ],

    }


    text_lower = (
        circular_text or ""
    ).lower()


    detected_entities = []


    for entity_name, patterns in entity_patterns.items():

        for pattern in patterns:

            if re.search(
                pattern,
                text_lower
            ):

                if entity_name not in detected_entities:

                    detected_entities.append(
                        entity_name
                    )

                break


    # Prefer actual entity categories detected
    # from the circular text.

    for entity in detected_entities:

        if entity not in cleaned:

            cleaned.append(
                entity
            )


    return cleaned


# ─────────────────────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────────────────────

def run_analysis(
    text,
    model,
    tfidf
):

    # TF-IDF

    vector = tfidf.transform(
        [text]
    )


    # Classification

    prediction = model.predict(
        vector
    )[0]


    # Confidence

    proba = model.predict_proba(
        vector
    )[0]

    classes = model.classes_


    confidence = dict(
        zip(
            classes,
            [
                round(
                    p * 100,
                    1
                )
                for p in proba
            ]
        )
    )


    # NLP extraction

    deadlines = extract_deadline(
        text
    )


    effective = extract_effective_date(
        text
    )


    penalty = detect_penalty(
        text
    )


    raw_entities = extract_entities(
        text
    )


    entities = clean_entities(
        raw_entities,
        text
    )


    keywords = extract_keywords(
        text
    )


    actions = extract_actions(
        text
    )


    summary = generate_summary(
        text
    )


    return {

        "prediction":
            prediction,

        "confidence":
            confidence,

        "deadlines":
            deadlines,

        "effective":
            effective,

        "penalty":
            penalty,

        "entities":
            entities,

        "keywords":
            keywords,

        "actions":
            actions,

        "summary":
            summary,
    }


# ─────────────────────────────────────────────────────────────
# TXT REPORT
# ─────────────────────────────────────────────────────────────

def build_txt_report(
    text,
    result
):

    effective_text = clean_effective_date(
        result["effective"]
    )


    lines = [

        "=" * 62,

        "RBI ALERT DESK — CIRCULAR ANALYSIS REPORT",

        f"Generated: "
        f"{datetime.now().strftime('%d %b %Y, %I:%M %p')}",

        "=" * 62,

        "",

        f"PREDICTION   : "
        f"{result['prediction']}",

        f"CONFIDENCE   : "
        f"{result['confidence']}",

        "",

        "DEADLINES:",

        *(
            [
                f"  • {d}"
                for d in result["deadlines"]
            ]

            or

            [
                "  None detected"
            ]
        ),

        "",

        f"EFFECTIVE DATE : "
        f"{effective_text}",

        "",

        f"PENALTY STATUS : "
        f"{result['penalty']}",

        "",

        "AFFECTED ENTITIES:",

        *(
            [
                f"  • {e}"
                for e in result["entities"]
            ]

            or

            [
                "  None detected"
            ]
        ),

        "",

        "KEYWORDS:",

        (
            "  "
            + ", ".join(
                result["keywords"]
            )

            if result["keywords"]

            else

            "  None"
        ),

        "",

        "COMPLIANCE ACTIONS:",

        *(
            [
                f"  - {a[:120]}"
                for a in result["actions"][:8]
            ]

            or

            [
                "  None detected"
            ]
        ),

        "",

        "SUMMARY:",

        result["summary"],

        "",

        "=" * 62,

        "SOURCE TEXT (first 500 chars):",

        text[:500]
        +
        (
            "..."
            if len(text) > 500
            else ""
        ),

        "=" * 62,
    ]


    return "\n".join(
        lines
    )


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────

def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div style='padding:.5rem 0 1.2rem'>

              <div style='font-size:1.5rem;
                          font-weight:700;
                          color:#F1F5F9;'>

                  🏦 RBI Alert Desk

              </div>

              <div style='font-size:.75rem;
                          color:#64748B;
                          margin-top:.2rem;'>

                AI Compliance Intelligence

              </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


        st.markdown(
            "### 👤 Developer"
        )


        st.markdown(
            """
            <div style='font-size:.88rem;
                        line-height:1.8;'>

              <b style='color:#F1F5F9;'>
                Atharva Desai
              </b><br>

              Data Science · NLP · FinTech

            </div>
            """,
            unsafe_allow_html=True,
        )


        st.markdown("---")


        st.markdown(
            "### 🤖 Model Info"
        )


        info_items = {

            "Classifier":
                "Random Forest",

            "Vectorizer":
                "TF-IDF",

            "Labels":
                "INFO / OPERATIONAL / URGENT",

            "Training set":
                "237 circulars",

            "Coverage":
                "2024 – 2026",
        }


        for k, v in info_items.items():

            st.markdown(
                f"""
                <div style='display:flex;
                            justify-content:space-between;
                            font-size:.8rem;
                            padding:.3rem 0;
                            border-bottom:
                            1px solid #1E293B;'>

                  <span style='color:#64748B;'>
                    {k}
                  </span>

                  <span style='color:#CBD5E1;
                               font-weight:500;'>
                    {v}
                  </span>

                </div>
                """,
                unsafe_allow_html=True,
            )


        st.markdown("---")


        st.markdown(
            "### 🏷 Label Guide"
        )


        labels = [

            (
                "🔴",
                "URGENT",
                "#DC3545",
                "Penalties, deadlines, enforcement",
            ),

            (
                "🟠",
                "OPERATIONAL",
                "#F59E0B",
                "KYC, frameworks, process changes",
            ),

            (
                "🟢",
                "INFO",
                "#198754",
                "Clarifications, announcements",
            ),
        ]


        for icon, lbl, color, desc in labels:

            st.markdown(
                f"""
                <div style='padding:.4rem 0;
                            font-size:.8rem;'>

                  <span style='color:{color};
                               font-weight:700;'>

                    {icon} {lbl}

                  </span>

                  <br>

                  <span style='color:#64748B;'>

                    {desc}

                  </span>

                </div>
                """,
                unsafe_allow_html=True,
            )


        st.markdown("---")


        st.markdown(
            "### 🔗 Links"
        )


        st.markdown(
            """
            <a class='nav-link'
               href='https://github.com/athhh07/RBI-AlertDesk'
               target='_blank'>

              📁 GitHub Repository

            </a>

            <a class='nav-link'
               href='https://www.linkedin.com/in/atharva-desai-3b24142a8'
               target='_blank'>

              💼 LinkedIn Profile

            </a>

            <a class='nav-link'
               href='https://www.rbi.org.in/Scripts/NotificationUser.aspx'
               target='_blank'>

              🏛 RBI Notifications

            </a>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────
# RESULT RENDERER
# ─────────────────────────────────────────────────────────────

def render_results(
    result,
    circular_text
):

    prediction = result["prediction"]

    confidence = result["confidence"]

    deadlines = result["deadlines"]

    effective = result["effective"]

    penalty = result["penalty"]

    entities = result["entities"]

    keywords = result["keywords"]

    actions = result["actions"]

    summary = result["summary"]


    # ─────────────────────────────────────────────────────────
    # PULSE BAR
    # ─────────────────────────────────────────────────────────

    pulse_cls = str(
        prediction
    ).lower()


    st.markdown(
        f"""
        <div class="pulse-bar {pulse_cls}">
        </div>
        """,
        unsafe_allow_html=True,
    )


    # ─────────────────────────────────────────────────────────
    # PREDICTION
    # ─────────────────────────────────────────────────────────

    pred_icons = {

        "URGENT":
            "🚨",

        "OPERATIONAL":
            "⚙️",

        "INFO":
            "ℹ️",
    }


    pred_cls = {

        "URGENT":
            "pred-urgent",

        "OPERATIONAL":
            "pred-operational",

        "INFO":
            "pred-info",
    }


    icon = pred_icons.get(
        prediction,
        "❓"
    )


    css_cls = pred_cls.get(
        prediction,
        "pred-info"
    )


    conf_val = confidence.get(
        prediction,
        0
    )


    col_badge, col_conf, col_spacer = st.columns(
        [2, 2, 3]
    )


    with col_badge:

        st.markdown(
            f"""
            <div style='margin-bottom:.5rem;'>

              <div class='card-label'>
                Classification Result
              </div>

              <div class='pred-badge {css_cls}'>

                {icon} {prediction}

              </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # ─────────────────────────────────────────────────────────
    # CONFIDENCE
    # ─────────────────────────────────────────────────────────

    with col_conf:

        st.markdown(
            """
            <div class='card-label'>
                Model Confidence
            </div>
            """,
            unsafe_allow_html=True,
        )


        st.markdown(
            f"""
            <div style="
                font-size:2rem;
                font-weight:700;
                color:#0F172A;
                margin-bottom:.7rem;
            ">
                {conf_val}%
            </div>
            """,
            unsafe_allow_html=True,
        )


        # IMPORTANT:
        # Only native Streamlit progress bars are used here.
        # No nested HTML confidence bars.

        sorted_confidence = sorted(
            confidence.items(),
            key=lambda x: -x[1]
        )


        for lbl, pct in sorted_confidence:

            st.caption(
                f"{lbl} — {pct}%"
            )


            st.progress(
                min(
                    max(
                        float(pct) / 100,
                        0.0
                    ),
                    1.0
                )
            )


    # ─────────────────────────────────────────────────────────
    # EXTRACTION RESULTS
    # ─────────────────────────────────────────────────────────

    st.markdown(
        '<div class="section-header">'
        'Extraction Results'
        '</div>',
        unsafe_allow_html=True,
    )


    c1, c2, c3 = st.columns(3)


    # ─────────────────────────────────────────────────────────
    # DEADLINES
    # ─────────────────────────────────────────────────────────

    with c1:

        st.markdown(
            """
            <div class='card'>

              <div class='card-label'>
                📅 Deadlines
              </div>
            """,
            unsafe_allow_html=True,
        )


        if deadlines:

            for d in deadlines[:5]:

                st.markdown(
                    f"""
                    <div class="deadline-item">

                      ⏰ {d}

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.markdown(
                """
                <div class="card-value"
                     style="color:#94A3B8;">

                  No explicit deadlines found

                </div>
                """,
                unsafe_allow_html=True,
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


    # ─────────────────────────────────────────────────────────
    # EFFECTIVE DATE
    # ─────────────────────────────────────────────────────────

    with c2:

        effective_text = clean_effective_date(
            effective
        )


        st.markdown(
            f"""
            <div class='card'>

              <div class='card-label'>
                🗓 Effective Date
              </div>

              <div class='card-value'>

                {effective_text}

              </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # ─────────────────────────────────────────────────────────
    # PENALTY
    # ─────────────────────────────────────────────────────────

    with c3:

        penalty_text = str(
            penalty
        )


        is_new = (
            "New penalty introduced"
            in penalty_text
        )


        is_hist = (
            "historical"
            in penalty_text.lower()
        )


        if is_new:

            pen_color = "#DC3545"

            pen_icon = "⚠️"

            pen_bg = "#FEF2F2"

        elif is_hist:

            pen_color = "#F59E0B"

            pen_icon = "📋"

            pen_bg = "#FFFBEB"

        else:

            pen_color = "#198754"

            pen_icon = "✅"

            pen_bg = "#F0FDF4"


        st.markdown(
            f"""
            <div class='card'>

              <div class='card-label'>
                ⚠️ Penalty Status
              </div>

              <div style='background:{pen_bg};
                          border-radius:8px;
                          padding:.6rem .8rem;
                          color:{pen_color};
                          font-size:.85rem;
                          font-weight:500;'>

                {pen_icon} {penalty_text}

              </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # ─────────────────────────────────────────────────────────
    # ENTITIES + KEYWORDS
    # ─────────────────────────────────────────────────────────

    c4, c5 = st.columns(
        [1, 1]
    )


    # ─────────────────────────────────────────────────────────
    # AFFECTED ENTITIES
    # ─────────────────────────────────────────────────────────

    with c4:

        st.markdown(
            """
            <div class='card'>

              <div class='card-label'>
                🏛 Affected Entities
              </div>

              <div class='tag-row'>
            """,
            unsafe_allow_html=True,
        )


        if entities:

            for entity in entities:

                st.markdown(
                    f"""
                    <span class="tag tag-entity">
                        {entity}
                    </span>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.markdown(
                """
                <span style="color:#94A3B8;
                              font-size:.85rem;">

                  No affected entities detected

                </span>
                """,
                unsafe_allow_html=True,
            )


        st.markdown(
            "</div></div>",
            unsafe_allow_html=True,
        )


    # ─────────────────────────────────────────────────────────
    # KEYWORDS
    # ─────────────────────────────────────────────────────────

    with c5:

        st.markdown(
            """
            <div class='card'>

              <div class='card-label'>
                🔑 Keywords
              </div>

              <div class='tag-row'>
            """,
            unsafe_allow_html=True,
        )


        if keywords:

            for kw in keywords:

                st.markdown(
                    f"""
                    <span class="tag">
                        {kw}
                    </span>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.markdown(
                """
                <span style="color:#94A3B8;
                              font-size:.85rem;">

                  No keywords detected

                </span>
                """,
                unsafe_allow_html=True,
            )


        st.markdown(
            "</div></div>",
            unsafe_allow_html=True,
        )


    # ─────────────────────────────────────────────────────────
    # COMPLIANCE ACTIONS
    # ─────────────────────────────────────────────────────────

    st.markdown(
        '<div class="section-header">'
        'Compliance Actions'
        '</div>',
        unsafe_allow_html=True,
    )


    with st.expander(
        "📋 View all compliance actions",
        expanded=True,
    ):

        if actions:

            for i, action in enumerate(
                actions[:10],
                1
            ):

                st.markdown(
                    f"""
                    <div class="action-item">

                      <b style="color:#0B5ED7;">
                        #{i}
                      </b>

                      {action[:200]}

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.info(
                "No specific compliance actions detected."
            )


    # ─────────────────────────────────────────────────────────
    # AI SUMMARY
    # ─────────────────────────────────────────────────────────

    st.markdown(
        '<div class="section-header">'
        'AI Summary'
        '</div>',
        unsafe_allow_html=True,
    )


    with st.expander(
        "📝 View circular summary",
        expanded=True,
    ):

        st.markdown(
            f"""
            <div style='background:#F8FAFC;
                        border-radius:10px;
                        padding:1rem 1.2rem;
                        font-size:.9rem;
                        line-height:1.7;
                        color:var(--text-1);
                        border:1px solid var(--border);'>

              {summary}

            </div>
            """,
            unsafe_allow_html=True,
        )


    # ─────────────────────────────────────────────────────────
    # EXPORT
    # ─────────────────────────────────────────────────────────

    st.markdown(
        '<div class="section-header">'
        'Export'
        '</div>',
        unsafe_allow_html=True,
    )


    dl_col1, dl_col2, _ = st.columns(
        [1.2, 1.2, 3]
    )


    txt_report = build_txt_report(
        circular_text,
        result,
    )


    with dl_col1:

        st.download_button(
            label="⬇️ Download TXT Report",
            data=txt_report,
            file_name=(
                "rbi_analysis_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                ".txt"
            ),
            mime="text/plain",
        )


    with dl_col2:

        st.download_button(
            label="⬇️ Download Raw Text",
            data=circular_text,
            file_name=(
                "circular_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                ".txt"
            ),
            mime="text/plain",
        )


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():

    render_sidebar()


    # ─────────────────────────────────────────────────────────
    # HERO
    # ─────────────────────────────────────────────────────────

    st.markdown(
        """
        <div class='hero'>

          <div class='hero-badge'>
            AI · NLP · RegTech · Banking
          </div>

          <div class='hero-title'>
            🏦 RBI Alert Desk
          </div>

          <div class='hero-sub'>

            AI-powered compliance intelligence for RBI circulars.
            Paste any RBI notification or upload a PDF and instantly
            get its classification, deadlines, penalties, affected
            entities, and a structured analysis — so your compliance
            team focuses on action, not reading.

          </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # ─────────────────────────────────────────────────────────
    # METRICS
    # ─────────────────────────────────────────────────────────

    m1, m2, m3, m4 = st.columns(4)


    metrics = [

        (
            m1,
            "📄",
            "Circulars Trained On",
            "237",
        ),

        (
            m2,
            "🏷",
            "Label Classes",
            "3",
        ),

        (
            m3,
            "🤖",
            "Classifier",
            "Random Forest",
        ),

        (
            m4,
            "📅",
            "Data Coverage",
            "2024 – 2026",
        ),
    ]


    for col, icon, label, value in metrics:

        col.markdown(
            f"""
            <div class='metric-tile'>

              <div class='metric-icon'>
                {icon}
              </div>

              <div class='metric-label'>
                {label}
              </div>

              <div class='metric-val'>
                {value}
              </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    # ─────────────────────────────────────────────────────────
    # INPUT
    # ─────────────────────────────────────────────────────────

    st.markdown(
        '<div class="section-header">'
        'Input — RBI Circular'
        '</div>',
        unsafe_allow_html=True,
    )


    input_method = st.radio(
        "Choose input method",
        [
            "📝 Paste Text",
            "📄 Upload PDF",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )


    circular_text = ""


    # ─────────────────────────────────────────────────────────
    # PASTE
    # ─────────────────────────────────────────────────────────

    if input_method == "📝 Paste Text":

        circular_text = st.text_area(

            label="Circular Text",

            placeholder=(
                "Paste the complete RBI Circular here...\n\n"
                "Include the full text for best extraction results."
            ),

            height=320,

            label_visibility="collapsed",

            key="circular_input",
        )


    # ─────────────────────────────────────────────────────────
    # PDF
    # ─────────────────────────────────────────────────────────

    else:

        uploaded_pdf = st.file_uploader(

            "Upload RBI Circular PDF",

            type=["pdf"],

            help=(
                "Upload a text-based RBI circular PDF "
                "for automatic text extraction."
            ),

            key="pdf_uploader",
        )


        if uploaded_pdf is not None:

            try:

                with st.spinner(
                    "Extracting text from PDF..."
                ):

                    circular_text = extract_text_from_pdf(
                        uploaded_pdf
                    )


                if circular_text.strip():

                    st.success(
                        "✅ PDF text extracted successfully — "
                        f"{len(circular_text.split()):,} words"
                    )


                    with st.expander(
                        "👁️ Preview extracted text"
                    ):

                        st.text(
                            circular_text[:5000]
                        )

                else:

                    st.error(
                        "❌ No selectable text was found in "
                        "this PDF. This may be a scanned/"
                        "image-only PDF."
                    )

                    circular_text = ""


            except Exception as e:

                st.error(
                    f"❌ Could not read the PDF: {e}"
                )

                circular_text = ""


    # ─────────────────────────────────────────────────────────
    # TEXT STATISTICS
    # ─────────────────────────────────────────────────────────

    char_count = len(
        circular_text
    )


    word_count = (

        len(
            circular_text.split()
        )

        if circular_text.strip()

        else 0
    )


    if circular_text.strip():

        st.markdown(
            f"""
            <div style='font-size:.72rem;
                        color:#94A3B8;
                        text-align:right;
                        margin-top:-.5rem;
                        margin-bottom:.8rem;'>

              {char_count:,} characters ·
              {word_count:,} words

            </div>
            """,
            unsafe_allow_html=True,
        )


    # ─────────────────────────────────────────────────────────
    # BUTTONS
    # ─────────────────────────────────────────────────────────

    btn_col1, btn_col2, _ = st.columns(
        [1, 1, 5]
    )


    analyze_clicked = btn_col1.button(
        "🔍 Analyze Circular",
        use_container_width=True,
    )


    clear_clicked = btn_col2.button(
        "✕ Clear",
        use_container_width=True,
    )


    # ─────────────────────────────────────────────────────────
    # CLEAR
    # ─────────────────────────────────────────────────────────

    if clear_clicked:

        st.session_state["circular_input"] = ""

        st.rerun()


    # ─────────────────────────────────────────────────────────
    # ANALYZE
    # ─────────────────────────────────────────────────────────

    if analyze_clicked:

        if not circular_text.strip():

            if input_method == "📝 Paste Text":

                st.warning(
                    "⚠️ Please paste a circular before "
                    "clicking Analyze."
                )

            else:

                st.warning(
                    "⚠️ Please upload a PDF before "
                    "clicking Analyze."
                )

            return


        if word_count < 20:

            st.warning(
                "⚠️ The text looks too short. "
                "Please provide the complete circular text."
            )

            return


        try:

            with st.spinner(
                "Analyzing circular — running "
                "classification and extraction..."
            ):

                model, tfidf = load_model()


                result = run_analysis(
                    circular_text,
                    model,
                    tfidf,
                )


            st.success(
                "✅ Analysis complete"
            )


            st.markdown(
                "---"
            )


            render_results(
                result,
                circular_text,
            )


        except FileNotFoundError as e:

            st.error(
                f"""
                ❌ Model file not found:

                {e}

                Make sure these files exist:

                `models/rbi_classifier.pkl`

                `models/tfidf_vectorizer.pkl`
                """
            )


        except Exception as e:

            st.error(
                f"""
                ❌ Analysis failed:

                {e}
                """
            )


# ─────────────────────────────────────────────────────────────
# RUN APP
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
