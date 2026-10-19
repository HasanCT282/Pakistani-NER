"""Single source of truth for entity types and ordered BIO labels."""

ENTITY_TYPES = (
    "PERSON", "CITY", "PROVINCE_REGION", "COUNTRY", "LANDMARK_FACILITY",
    "GOVERNMENT_BODY", "POLITICAL_PARTY", "ORGANIZATION",
    "EDUCATIONAL_INSTITUTION", "COURT_LEGAL_BODY", "LAW_ACT", "EVENT",
    "MEDIA_OUTLET", "SPORTS_TEAM", "DATE", "TIME", "MONEY", "PERCENT",
    "PHONE_NUMBER", "ID_NUMBER",
)
BIO_LABELS = ("O",) + tuple(
    f"{prefix}-{entity}" for entity in ENTITY_TYPES for prefix in ("B", "I")
)
LABEL_TO_ID = {label: index for index, label in enumerate(BIO_LABELS)}
ID_TO_LABEL = {index: label for label, index in LABEL_TO_ID.items()}
