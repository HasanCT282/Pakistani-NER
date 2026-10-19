# Annotation format

This is the project's internal format; adapt future competition data to it after
checking the official dataset specification. No official format is assumed.

Use UTF-8 JSONL: exactly one JSON object per line, with no blank lines.
Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| id | Nonempty string | Unique example identifier |
| tokens | Nonempty array of nonempty strings | Tokens in original reading order |
| ner_tags | Nonempty array of strings | One BIO label per token |

Optional metadata is permitted but not validated. Token boundaries are explicit:
punctuation may be separate tokens, multiword entities use multiple tokens, and
the same tokenization convention should be used throughout a dataset. No raw
text or character offsets are required. English, Urdu, and Roman Urdu strings
are supported. The validator does not retokenize or normalize them.

## BIO conventions

`O` marks a token outside an entity. `B-TYPE` starts an entity; `I-TYPE`
continues the immediately preceding entity of the same type. An `I-` tag cannot
start a sentence, follow `O`, or continue a different type. Adjacent distinct
entities each start with `B-`, even when their types match. This flat format
cannot represent overlapping or nested entities; annotate one span per token.
Token indexes in diagnostic messages start at zero; file line numbers start at one.

`config/labels.py` is the authoritative ordered vocabulary: exactly 20 entity
types and 41 labels including `O`. Label IDs follow that order; preserve it
when later saving model configurations.

Types: PERSON, CITY, PROVINCE_REGION, COUNTRY, LANDMARK_FACILITY,
GOVERNMENT_BODY, POLITICAL_PARTY, ORGANIZATION, EDUCATIONAL_INSTITUTION,
COURT_LEGAL_BODY, LAW_ACT, EVENT, MEDIA_OUTLET, SPORTS_TEAM, DATE, TIME,
MONEY, PERCENT, PHONE_NUMBER, ID_NUMBER.

## Synthetic examples

All sentences in `data/synthetic_sample.jsonl` are constructed demonstrations.
Place names and institutions can refer to actual entities; described events
are fictional. Phone and ID values are deliberately invalid placeholders,
not actual phone numbers or CNICs. Never replace them with real people's data.
These placeholders demonstrate tags, not realistic numeric distributions.

```jsonl
{"id":"demo-city","tokens":["Lahore","is","in","Punjab","."],"ner_tags":["B-CITY","O","O","B-PROVINCE_REGION","O"]}
{"id":"demo-private","tokens":["Phone",":","03XX-0000000","ID",":","XXXXX-0000000-X"],"ner_tags":["O","O","B-PHONE_NUMBER","O","O","B-ID_NUMBER"]}
```

Exact duplicate token sequences are rejected regardless of IDs or annotations,
which also catches conflicting annotations of identical examples. Duplicate
checking is exact and case-sensitive within one file; near duplicates and
cross-file overlap require separate later checks. Semantic span correctness
and fine distinctions between institution types require human review.
