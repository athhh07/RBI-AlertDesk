import re

# =============================================================================
# DEADLINE EXTRACTION
# =============================================================================

MONTH_NAMES = (
    "january|february|march|april|may|june|"
    "july|august|september|october|november|december"
)

DEADLINE_PATTERNS = [
    r"within\s+\d+\s+(?:days?|months?|weeks?|years?)",

    r"within\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|"
    r"fifteen|thirty|sixty|ninety)\s+(?:days?|months?|weeks?|years?)",

    r"not later than\s+[^.\n]{3,60}",

    r"on or before\s+(?:" + MONTH_NAMES + r")\s+\d{1,2},?\s*\d{4}",

    r"before\s+(?:" + MONTH_NAMES + r")\s+\d{1,2},?\s*\d{4}",

    r"by\s+(?:" + MONTH_NAMES + r")\s+\d{1,2},?\s*\d{4}",

    r"by\s+(?:" + MONTH_NAMES + r")\s+\d{4}",

    r"by\s+\d{1,2}(?:st|nd|rd|th)?\s+(?:" + MONTH_NAMES + r"),?\s*\d{4}",

    r"by\s+(?:the\s+)?end\s+of\s+[^.\n]{3,40}",

    r"within\s+(?:the\s+)?(?:current\s+)?financial\s+year\s*\d{4}[-–]\d{2,4}",

    r"with\s+immediate\s+effect",

    r"immediate\s+effect",

    r"shall\s+come\s+into\s+(?:effect|force)\s+(?:from\s+)?[^.\n]{3,50}",

    r"by\s+\d{1,2}[./]\d{1,2}[./]\d{2,4}"
]


def extract_deadline(text):
    """
    Extract deadline-related phrases from RBI circular.
    """
    if not text:
        return []

    results = []
    lower_text = str(text).lower()

    for pattern in DEADLINE_PATTERNS:
        matches = re.findall(pattern, lower_text, re.IGNORECASE)
        results.extend(matches)

    seen = set()
    unique = []

    for item in results:
        item = re.sub(r"\s+", " ", item).strip()

        if item not in seen and len(item) > 3:
            seen.add(item)
            unique.append(item)

    return unique


# =============================================================================
# EFFECTIVE DATE EXTRACTION
# =============================================================================

EFFECTIVE_PHRASES = [
    r"with\s+(?:immediate\s+)?effect\s+from\s+[^.\n]{3,50}",

    r"effective\s+from\s+[^.\n]{3,50}",

    r"shall\s+take\s+effect\s+(?:from\s+)?[^.\n]{3,50}",

    r"shall\s+be\s+effective\s+(?:from\s+)?[^.\n]{3,50}",

    r"shall\s+come\s+into\s+(?:effect|force)\s+(?:from\s+|on\s+)?[^.\n]{3,50}",

    r"come\s+into\s+force\s+(?:from\s+|on\s+)?[^.\n]{3,50}",

    r"with\s+immediate\s+effect",

    r"immediate\s+effect",

    r"placed\s+on\s+the\s+official\s+website[^.\n]{0,60}"
]

ISSUE_DATE_PATTERN = re.compile(
    r"(?:^|\n)\s*("
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s+\d{1,2},?\s+\d{4}"
    r")\s*(?:\n|$)",
    re.IGNORECASE | re.MULTILINE
)


def extract_effective_date(text, circular_date=None):
    """
    Extract effective date information.
    """

    if not text:
        return {
            "explicit_phrases": [],
            "effective_date": "Not specified",
            "source": "none"
        }

    lower = str(text).lower()
    found = []

    for pattern in EFFECTIVE_PHRASES:
        matches = re.findall(pattern, lower, re.IGNORECASE)
        found.extend(matches)

    found = list(dict.fromkeys(
        re.sub(r"\s+", " ", p).strip()
        for p in found
    ))

    if found:
        return {
            "explicit_phrases": found,
            "effective_date": found[0],
            "source": "explicit"
        }

    match = ISSUE_DATE_PATTERN.search(str(text))

    if match:
        return {
            "explicit_phrases": [],
            "effective_date": match.group(1) + " (effective from date of issue)",
            "source": "issue_date_from_text"
        }

    if circular_date is not None:
        return {
            "explicit_phrases": [],
            "effective_date": str(circular_date) + " (effective from date of issue)",
            "source": "circular_date_column"
        }

    return {
        "explicit_phrases": [],
        "effective_date": "Not specified",
        "source": "none"
    }

# =============================================================================
# PENALTY DETECTION
# =============================================================================

NEW_PENALTY_PATTERNS = [
    r"₹\s*[\d,]+",
    r"penalty\s+(?:of|@)\s+₹",
    r"penalty\s+shall\s+be\s+levied",
    r"penalty\s+will\s+be\s+levied",
    r"levy\s+(?:of\s+)?penalty",
    r"impose\s+(?:a\s+)?(?:monetary\s+)?penalty",
    r"monetary\s+penalty",
    r"liable\s+to\s+pay",
    r"liable\s+to\s+a\s+penalty",
    r"prosecution\s+under\s+section",
    r"enforcement\s+action",
    r"fine\s+of\s+₹",
    r"recovery\s+of\s+loss\s+and\s+levy",
    r"wilful\s+(?:involvement|default|negligence)"
]

HISTORICAL_PENALTY_PHRASES = [
    "shall not in any way prejudicially affect",
    "any penalty, forfeiture, or punishment incurred",
    "penalties already imposed",
    "notwithstanding such repeal",
    "penalty incurred in respect of any contravention committed thereunder",
]


def detect_penalty(text):
    """
    Detect whether the circular introduces a new penalty or only
    references an existing/historical penalty.
    """

    if not text:
        return "NO"

    lower = str(text).lower()

    for pattern in NEW_PENALTY_PATTERNS:
        if re.search(pattern, lower):
            return "YES - New penalty introduced"

    for phrase in HISTORICAL_PENALTY_PHRASES:
        if phrase in lower:
            return "YES - Penalty referenced (historical context only)"

    generic_words = [
        "penalty",
        "fine",
        "non-compliance",
        "liable",
        "prosecution",
        "contravention"
    ]

    for word in generic_words:
        if word in lower:
            return "YES - Penalty referenced (context unclear)"

    return "NO"


# =============================================================================
# ENTITY EXTRACTION
# =============================================================================

ENTITY_PATTERNS = [
    r"all\s+([A-Za-z][A-Za-z\s&\-/]{3,80})",
    r"scheduled commercial banks",
    r"co-operative banks",
    r"urban co-operative banks",
    r"small finance banks",
    r"payments banks",
    r"local area banks",
    r"housing finance companies",
    r"non-banking financial companies",
    r"nbfcs",
    r"primary dealers",
    r"authorised dealer banks",
    r"asset reconstruction companies",
    r"mortgage guarantee companies",
    r"credit information companies",
    r"regulated entities",
    r"banks",
]


def extract_entities(text):
    """
    Extract affected institutions/entities.
    """

    if not text:
        return []

    lower = str(text).lower()

    entities = []

    for pattern in ENTITY_PATTERNS:

        matches = re.findall(pattern, lower, re.IGNORECASE)

        if isinstance(matches, list):

            for m in matches:

                if isinstance(m, tuple):
                    m = " ".join(m)

                m = str(m).strip()

                if len(m) > 2:
                    entities.append(m.title())

    entities = sorted(set(entities))

    return entities[:10]


# =============================================================================
# KEYWORD EXTRACTION
# =============================================================================

KEYWORDS = [
    "penalty",
    "deadline",
    "compliance",
    "capital",
    "investment",
    "bank",
    "customer",
    "credit",
    "payment",
    "transfer",
    "cyber",
    "risk",
    "fraud",
    "outsourcing",
    "dividend",
    "reporting",
    "governance",
    "liquidity",
    "foreign",
    "deposit",
    "loan",
    "interest",
    "security",
    "sanction",
    "uapa",
    "green",
    "digital",
    "amendment",
    "licensing",
    "branch",
]


def extract_keywords(text):
    """
    Return important keywords present in the circular.
    """

    if not text:
        return []

    lower = str(text).lower()

    found = []

    for word in KEYWORDS:
        if word in lower:
            found.append(word.title())

    return sorted(set(found))

# =============================================================================
# COMPLIANCE ACTION EXTRACTION
# =============================================================================

ACTION_PATTERNS = [
    r"shall\s+[^.]{10,200}",
    r"must\s+[^.]{10,200}",
    r"required\s+to\s+[^.]{10,200}",
    r"required\s+[^.]{10,200}",
    r"ensure\s+that\s+[^.]{10,200}",
    r"banks\s+shall\s+[^.]{10,200}",
    r"regulated\s+entities\s+shall\s+[^.]{10,200}",
    r"ad\s+category\s*[- ]?i\s+banks\s+shall\s+[^.]{10,200}",
]


def extract_actions(text):
    """
    Extract compliance actions from the circular.
    Returns a list of important action statements.
    """

    if not text:
        return []

    actions = []

    clean_text = re.sub(r"\s+", " ", str(text))

    for pattern in ACTION_PATTERNS:
        matches = re.findall(pattern, clean_text, re.IGNORECASE)

        for match in matches:

            sentence = match.strip()

            sentence = re.sub(r"\s+", " ", sentence)

            if len(sentence) > 30:
                actions.append(sentence)

    # Remove duplicates while preserving order
    unique = []

    seen = set()

    for action in actions:

        if action not in seen:

            seen.add(action)

            unique.append(action)

    return unique[:10]


# =============================================================================
# SUMMARY GENERATION
# =============================================================================

def generate_summary(text, max_sentences=3):
    """
    Generate a simple extractive summary by selecting
    the first few meaningful sentences.
    """

    if not text:
        return ""

    clean = re.sub(r"\s+", " ", str(text)).strip()

    sentences = re.split(r'(?<=[.!?])\s+', clean)

    summary = []

    for sentence in sentences:

        sentence = sentence.strip()

        if len(sentence) < 40:
            continue

        # Ignore common headers
        lower = sentence.lower()

        if any(skip in lower for skip in [
            "reserve bank of india",
            "www.rbi.org.in",
            "rbi/",
            "table of contents"
        ]):
            continue

        summary.append(sentence)

        if len(summary) >= max_sentences:
            break

    return " ".join(summary)


# =============================================================================
# END OF FILE
# =============================================================================