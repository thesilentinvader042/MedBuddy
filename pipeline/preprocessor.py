import re

STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "what", "how",
             "why", "when", "can", "could", "would", "should", "does"}

# Extended SNOMED synonym map for clinical and layperson terms
SNOMED_MAP = {
    # --- Original Entries ---
    "heart attack": "myocardial infarction",
    "high blood pressure": "hypertension",
    "sugar disease": "diabetes mellitus",
    "water on the brain": "hydrocephalus",
    "fits": "seizures",
    "tb": "tuberculosis",
    "bp": "blood pressure",
    "mi": "myocardial infarction",
    "copd": "chronic obstructive pulmonary disease",
    "uti": "urinary tract infection",
    "cxr": "chest X-ray",

    # --- Cardiovascular & Blood ---
    "stroke": "cerebrovascular accident",
    "cva": "cerebrovascular accident",
    "afib": "atrial fibrillation",
    "heart failure": "congestive heart failure",
    "chf": "congestive heart failure",
    "chest pain": "angina pectoris",
    "blood clot in leg": "deep vein thrombosis",
    "dvt": "deep vein thrombosis",
    "low iron": "iron deficiency anemia",
    "clogged arteries": "atherosclerosis",

    # --- Respiratory ---
    "shortness of breath": "dyspnea",
    "doe": "dyspnea on exertion",
    "runny nose": "rhinorrhea",
    "sore throat": "pharyngitis",
    "pe": "pulmonary embolism",
    "rsv": "respiratory syncytial virus",
    "hay fever": "allergic rhinitis",

    # --- Gastrointestinal ---
    "heartburn": "gastroesophageal reflux disease",
    "gerd": "gastroesophageal reflux disease",
    "stomach flu": "gastroenteritis",
    "gallstones": "cholelithiasis",
    "piles": "hemorrhoids",
    "bloody stool": "hematochezia",
    "difficulty swallowing": "dysphagia",

    # --- Neurological & ENT ---
    "pins and needles": "paresthesia",
    "dizzy": "vertigo",
    "ringing in ears": "tinnitus",
    "ear infection": "otitis media",
    "double vision": "diplopia",
    "fainting": "syncope",
    "concussion": "traumatic brain injury",

    # --- Musculoskeletal & Skin ---
    "broken bone": "fracture",
    "fx": "fracture",
    "slipped disc": "herniated nucleus pulposus",
    "tennis elbow": "lateral epicondylitis",
    "hives": "urticaria",
    "itchy": "pruritus",
    "shingles": "herpes zoster",

    # --- Clinical Signs & Abbreviations ---
    "fever": "pyrexia",
    "yellow skin": "jaundice",
    "armpit": "axilla",
    "nosebleed": "epistaxis",
    "npo": "nothing by mouth",
    "prn": "as needed",
    "stat": "immediately",
}

def normalize(query: str) -> tuple[str, list[str]]:
    """
    Returns (normalized_query, extracted_entities).
    Entities: drug names, diseases, symptoms, tests found in the query.
    """
    q = query.lower().strip()

    # Spelling-level normalization for common typos
    q = re.sub(r'\bcetirizne\b', 'cetirizine', q)
    q = re.sub(r'\bparacetmol\b', 'paracetamol', q)
    q = re.sub(r'\bmetformine\b', 'metformin', q)

    # SNOMED mapping
    for colloquial, medical in SNOMED_MAP.items():
        q = re.sub(rf'\b{re.escape(colloquial)}\b', medical, q)

    # Remove stopwords (keep for meaning, strip for entity extraction)
    tokens = q.split()
    entities = [t for t in tokens if t not in STOPWORDS and len(t) > 2]

    # Compact representation: remove redundant whitespace
    q = re.sub(r'\s+', ' ', q).strip()

    return q, entities