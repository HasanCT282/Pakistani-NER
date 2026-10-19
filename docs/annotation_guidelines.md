# Annotation guidelines

These are project annotation conventions, not verified official competition
rules. Use exactly the types in `config/labels.py` and the JSONL contract in
[annotation_format.md](annotation_format.md). All example sentences are
constructed; they do not assert real events. Phone and CNIC examples below
are deliberately masked, synthetic placeholders and identify nobody.

## Shared span and BIO rules

- Annotate explicit mentions only, using the spelling in the source. Do not
  expand abbreviations, correct spelling, translate, or infer missing names.
  Apply the same rules to English, Urdu, and Roman Urdu.
- Use the shortest complete name or numeric expression identifying the entity.
  Include internal function words and punctuation belonging to a name. Exclude
  surrounding quotes, sentence punctuation, articles, possessive endings,
  postpositions, and descriptive phrases unless part of the actual name.
- Personal titles, job titles, and generic nouns are outside spans. A generic
  institution word belongs inside when part of its name, such as `University`
  in `University of Karachi`. Pronouns and unnamed references remain `O`.
- Use one contiguous span per mention. Never cross sentence boundaries. Split
  coordinated mentions: `Lahore and Karachi` gives two CITY spans; `and` is O.
- No nested or overlapping annotations. A complete named institution, event,
  law, team, or facility takes priority over embedded place/person names.
  `University of Karachi` is one EDUCATIONAL_INSTITUTION, with no nested CITY.
  An independent location qualifier outside the name is labeled separately.
- Token boundaries must support the spans. Prefer separating external
  punctuation and possessive endings during data preparation. Do not split
  an existing token through tagging; flag inseparable boundary problems for
  review. Keep numeric separators and internal name hyphens inside the span.
- First token: `B-TYPE`; subsequent tokens in that same mention: `I-TYPE`.
  Everything else: `O`. Adjacent separate mentions each start with B, even
  when their types match. One-token entities have only a B tag.
- In examples, `[text](TYPE)` indicates a span, not literal JSONL syntax.
  Examples are annotation illustrations and are not a dataset to append.

For example:

```json
{"id":"guideline-demo","tokens":["University","of","Karachi","is","in","Karachi","."],"ner_tags":["B-EDUCATIONAL_INSTITUTION","I-EDUCATIONAL_INSTITUTION","I-EDUCATIONAL_INSTITUTION","O","O","B-CITY","O"]}
```

## Institution classification and precedence

Classify by the named referent and its function in context, not ownership or
words such as `Pakistan`, `National`, `Board`, or `Authority` alone.

| Referent | Label | Boundary decision |
| --- | --- | --- |
| Named political party | POLITICAL_PARTY | Includes full party name and faction suffix |
| Named court, tribunal, or judicial/legal adjudicatory body | COURT_LEGAL_BODY | Includes court level and location when part of name |
| Named university, college, school, or teaching institution | EDUCATIONAL_INSTITUTION | Applies to public and private institutions |
| Named newspaper, channel, news agency, or editorial outlet | MEDIA_OUTLET | Includes outlet brand, not every corporate owner |
| Named ministry, legislature, department, regulator, or public authority | GOVERNMENT_BODY | Applies when none of the more specific classes above fits |
| Other named company, charity, association, or institution | ORGANIZATION | Fallback for actual organizations, not uncertain spans |

SPORTS_TEAM applies to the playing team; a sports governing board is an
ORGANIZATION under this project's convention. Public ownership alone does not
make a commercial company GOVERNMENT_BODY. Hospitals and research institutes
without a clear teaching-institution identity are ORGANIZATION. A party's named
internal wing follows POLITICAL_PARTY only if explicitly named as a party unit;
an independently named affiliated organization follows its own function.

Use the institution type for an institution acting, speaking, employing, or
admitting students. Use LANDMARK_FACILITY for an explicitly named building,
venue, campus, or complex as a physical site. A plain institution name after
`at` remains its institution type unless the text clearly denotes a named
physical facility. Do not switch types solely because of the preposition.
Unclear identities go to human review; do not silently default to ORGANIZATION.

## PERSON

- **Qualifies:** Named individual people, including surnames or aliases when
  context identifies an individual. Fictional people are eligible.
- **Exclude:** Pronouns, occupations, unnamed relatives, honorifics, and groups.
- **Boundaries:** Include given names, surnames, initials, and name particles;
  exclude `Dr.`, `Mr.`, `Justice`, `Captain`, and accompanying job titles.
- **Examples:** `Dr. [Ayesha Khan](PERSON) spoke in [Lahore](CITY).`;
  `[Bilal Ahmed](PERSON) travelled to [Quetta](CITY).` Both people are fictional.
- **Ambiguity:** A person name inside a complete facility or organization name
  is not separately tagged. `Khan` alone is PERSON only with clear individual
  reference; a title or surname-like ordinary word without context is O.

## CITY

- **Qualifies:** Named cities, towns, and settlements, including clear aliases.
- **Exclude:** Provinces, districts as administrative units, street names,
  demonyms such as `Lahori`, and generic `the city`.
- **Boundaries:** Include the full settlement name; exclude descriptive `city`
  unless part of the proper name. Do not include an adjoining province.
- **Examples:** `[Lahore](CITY) hosted a workshop.`;
  `The visitors reached [Dera Ismail Khan](CITY).`
- **Ambiguity:** `Islamabad` as a settlement is CITY; explicit `Islamabad Capital
  Territory` as an administrative region is PROVINCE_REGION. `Karachi district`
  as a unit is PROVINCE_REGION; the city's standalone name is CITY.

## PROVINCE_REGION

- **Qualifies:** Named provinces, territories, administrative districts and
  divisions, and explicitly named geographic regions under this project policy.
- **Exclude:** Settlements, countries, unnamed `the region`, and demonyms.
- **Boundaries:** Include administrative designators attached to an explicit
  unit, e.g. `Lahore District`; exclude surrounding `province of` unless it
  belongs to the written proper name.
- **Examples:** `Rain reached [Sindh](PROVINCE_REGION).`;
  `The route crosses [Gilgit-Baltistan](PROVINCE_REGION).`
- **Ambiguity:** Use context to distinguish city from district. Label geographic
  references as written without making claims about sovereignty or boundaries.
  Constituency codes and street addresses have no dedicated type; do not force
  them into this class. Unclear region-versus-feature cases need review.

## COUNTRY

- **Qualifies:** Explicit country names and unambiguous country abbreviations.
- **Exclude:** Nationality adjectives, languages, flags, and unnamed governments.
- **Boundaries:** Include complete official names when written; exclude articles
  and modifiers outside the name.
- **Examples:** `The shipment reached [Pakistan](COUNTRY).`;
  `A delegation from [Pakistan](COUNTRY) visited [China](COUNTRY).`
- **Ambiguity:** `Pakistani` alone is O. `Pakistan announced ...` remains COUNTRY
  as country metonymy; `Government of Pakistan` is GOVERNMENT_BODY. Pakistan
  inside a complete team or institution name receives no nested COUNTRY span.

## LANDMARK_FACILITY

- **Qualifies:** Named monuments, buildings, roads, bridges, airports, stations,
  stadiums, parks, and explicitly named physical campuses or complexes.
- **Exclude:** Generic `the airport`, unnamed buildings, entire cities, and
  natural features without an applicable region interpretation.
- **Boundaries:** Include the full facility name and integral facility words;
  exclude directions and nearby location qualifiers outside the name.
- **Examples:** `They visited [Minar-e-Pakistan](LANDMARK_FACILITY).`;
  `The meeting took place at [Gaddafi Stadium](LANDMARK_FACILITY).`
- **Ambiguity:** A named hospital as a care organization is ORGANIZATION; an
  explicitly named hospital building as a physical site is LANDMARK_FACILITY.
  Use the shared institution/site rule. Rivers and mountains are not facilities;
  do not force them into this type merely because they are famous.

## GOVERNMENT_BODY

- **Qualifies:** Named governments, ministries, departments, legislatures,
  public regulators, police bodies, and administrative authorities.
- **Exclude:** Individual officeholders, generic `the ministry`, parties,
  courts, universities, and public companies acting as commercial enterprises.
- **Boundaries:** Include full official body names, including geographic parts
  of that name; exclude introductory `the` and officeholder titles.
- **Examples:** `[Election Commission of Pakistan](GOVERNMENT_BODY) issued a notice.`;
  `[Punjab Police](GOVERNMENT_BODY) announced a campaign.`
- **Ambiguity:** `Government of Sindh` is one GOVERNMENT_BODY; `Sindh` alone
  stays PROVINCE_REGION even when used metonymically. A legal regulator is
  GOVERNMENT_BODY unless its referent is specifically an adjudicatory body.

## POLITICAL_PARTY

- **Qualifies:** Named political parties, established abbreviations, and
  explicitly named internal party units under the shared policy.
- **Exclude:** Politicians, unnamed coalitions, political ideologies, and
  generic `the opposition` or `the party`.
- **Boundaries:** Include integral faction markers and parenthetical faction
  suffixes, e.g. the `(N)` in a written party name. Exclude generic supporters.
- **Examples:** `[Pakistan Peoples Party](POLITICAL_PARTY) held a meeting.`;
  `[Pakistan Tehreek-e-Insaf](POLITICAL_PARTY) issued a statement.`
- **Ambiguity:** `PPP` or `PTI` receives this type only when context supports the
  party sense. A separately named political alliance is ORGANIZATION unless
  established in the corpus as a party; unresolved identity needs review.

## ORGANIZATION

- **Qualifies:** Named companies, NGOs, charities, professional associations,
  nonteaching research institutes, and sports governing associations.
- **Exclude:** Generic groups, products, public authorities, and every referent
  covered by a more specific institutional type.
- **Boundaries:** Include integral corporate suffixes when written; exclude
  descriptive industry words and location qualifiers outside the name.
- **Examples:** `[Edhi Foundation](ORGANIZATION) organized a drive.`;
  `[Pakistan Cricket Board](ORGANIZATION) announced a workshop.`
- **Ambiguity:** A board governing a sport is ORGANIZATION, while its playing
  team is SPORTS_TEAM. A news outlet's separately named corporate parent is
  ORGANIZATION; the editorial brand is MEDIA_OUTLET. Unknown identity is review
  work, not sufficient evidence for this fallback label.

## EDUCATIONAL_INSTITUTION

- **Qualifies:** Named schools, colleges, universities, and clearly identified
  teaching institutions, whether publicly or privately operated.
- **Exclude:** Generic `the university`, degrees, courses, student groups,
  education ministries, and research-only organizations.
- **Boundaries:** Include the complete institution name and integral campus
  qualifier when used as the institution's name; avoid nested CITY tags.
- **Examples:** `[University of Karachi](EDUCATIONAL_INSTITUTION) opened admissions.`;
  `[NUST](EDUCATIONAL_INSTITUTION) hosted a seminar.`
- **Ambiguity:** An education regulator is GOVERNMENT_BODY. A named physical
  campus site follows LANDMARK_FACILITY when clearly a facility reference.
  A faculty or department named together with its university is one complete
  EDUCATIONAL_INSTITUTION span; generic `the department` is O.

## COURT_LEGAL_BODY

- **Qualifies:** Named courts, tribunals, benches with identifying court names,
  and adjudicatory legal institutions.
- **Exclude:** Individual judges, law firms, statutes, generic `the court`,
  police, and administrative regulators without adjudicatory reference.
- **Boundaries:** Include full court name, jurisdiction, and named bench
  qualifier when contiguous; exclude titles of judges appearing beside it.
- **Examples:** `[Supreme Court of Pakistan](COURT_LEGAL_BODY) heard a petition.`;
  `[Lahore High Court](COURT_LEGAL_BODY) listed a hearing.`
- **Ambiguity:** A named court as an institution keeps this type; an explicitly
  named court building as a venue follows LANDMARK_FACILITY. Bar associations
  and law firms are ORGANIZATION under this policy; regulators are generally
  GOVERNMENT_BODY. Flag mixed adjudicatory/regulatory bodies for review.

## LAW_ACT

- **Qualifies:** Named acts, ordinances, constitutions, rules, regulations, and
  explicit legal instrument citations identifying a particular instrument.
- **Exclude:** Generic `the law`, case names, petitions, informal policies,
  and isolated section numbers that do not identify an instrument.
- **Boundaries:** Include the full title, integral year, and internal comma.
  In `section 5 of the [Elections Act, 2017](LAW_ACT)`, label only the law title.
  In `Article 25 of the [Constitution of Pakistan](LAW_ACT)`, label only
  `Constitution of Pakistan`; `Article 25 of` and `the` stay O.
- **Examples:** `They discussed the [Elections Act, 2017](LAW_ACT).`;
  `The lesson covered the [Constitution of Pakistan](LAW_ACT).`
- **Ambiguity:** The year within a law title is not a nested DATE.
  `Article 25` stays O, including when followed by an explicit instrument name;
  label only the instrument title as above. Flag unclear references if needed.

## EVENT

- **Qualifies:** Named festivals, tournaments, conferences, campaigns, and
  identifiable scheduled or historical events with a conventional name.
- **Exclude:** Generic meetings, matches, accidents, and `the election` without
  an identifying event name.
- **Boundaries:** Include integral edition, year, and sponsor when part of the
  written event title. Exclude separate date/location descriptions.
- **Examples:** `[Pakistan Super League](EVENT) attracted visitors.`;
  `[TechFest](EVENT) hosted a workshop in [Islamabad](CITY).`
- **Ambiguity:** `PSL` is EVENT in tournament context; an individual team is
  SPORTS_TEAM. A year attached as an edition belongs inside the event span;
  `TechFest in 2026` gives EVENT, O, DATE. An unnamed recurring activity is O.

## MEDIA_OUTLET

- **Qualifies:** Named newspapers, television/radio outlets, news agencies,
  and identifiable digital editorial publications.
- **Exclude:** Individual journalists, generic `the media`, social platforms,
  and separately named corporate holding companies.
- **Boundaries:** Include the full outlet brand and integral `News`, `TV`, or
  similar words; exclude an article introducing the brand.
- **Examples:** `[Dawn](MEDIA_OUTLET) published a report.`;
  `[Geo News](MEDIA_OUTLET) covered the workshop.`
- **Ambiguity:** `dawn` meaning daybreak is O. Public broadcasting ownership
  does not override MEDIA_OUTLET. A social platform is ORGANIZATION when used
  as a company, and O when merely a product/service with no organizational sense.

## SPORTS_TEAM

- **Qualifies:** Named playing teams, franchises, and national or regional
  representative sides with clear team reference.
- **Exclude:** Individual athletes, leagues, tournaments, governing boards,
  unnamed `the team`, and generic fans.
- **Boundaries:** Include full team names and identifying age/gender qualifiers
  attached to a named side; do not label embedded city names separately.
- **Examples:** `[Lahore Qalandars](SPORTS_TEAM) played a match.`;
  `[Karachi Kings](SPORTS_TEAM) announced a squad.`
- **Ambiguity:** `Pakistan won the match` is SPORTS_TEAM when clearly the playing
  side; otherwise Pakistan is COUNTRY. `Pakistan cricket team` is a complete
  SPORTS_TEAM span. Distinguish the governing board (ORGANIZATION) from its team.

## DATE

- **Qualifies:** Calendar dates, named days/months, years used temporally,
  explicit date ranges, and relative calendar expressions such as `tomorrow`.
- **Exclude:** Durations (`three days`), ages, academic/model numbers, and
  years already inside named laws/events.
- **Boundaries:** Include day/month/year and internal separators or range
  connectors; exclude surrounding `on`, `in`, and `from`. `12 to 14 March 2026`
  is one DATE; `from 12 March to 14 March` has DATE, O, DATE after the initial O.
- **Examples:** `The [Lahore](CITY) session is on [12 March 2026](DATE).`;
  `The [Karachi](CITY) workshop starts [tomorrow](DATE).`
- **Paired range examples:** `The workshop runs [12 to 14 March 2026](DATE).`;
  `The workshop runs from [12 March](DATE) to [14 March](DATE).`
  In the second example, `from` and `to` stay O.
- **Ambiguity:** Preserve ambiguous numeric dates such as `03/04/2026` as DATE
  when context is temporal; do not guess or normalize day/month order. `May`
  needs calendar context. `2026` as an identifier is not automatically DATE.

## TIME

- **Qualifies:** Clock times, named clock points such as `noon`, and explicit
  clock ranges. Include written AM/PM and timezone markers when supplied.
- **Exclude:** Durations (`two hours`), vague periods (`evening`), and bare
  numbers without clock context.
- **Boundaries:** Include time digits, colon, AM/PM, and timezone in the same
  contiguous expression; exclude `at` and other surrounding prepositions.
  `10:00-11:00 AM` is one TIME; intervening external prepositions split spans.
- **Examples:** `The [Lahore](CITY) talk begins at [10:00 AM](TIME).`;
  `The [Karachi](CITY) call is at [14:30 PKT](TIME).`
- **Ambiguity:** `at 5` is TIME only with a clear clock meaning. `10 March at
  5 PM` gives DATE, O, TIME. `morning` remains O under this project convention.

## MONEY

- **Qualifies:** Explicit monetary amounts with a currency marker or an
  unambiguous currency word. Accept PKR, Rs, Rs., rupees, and Urdu equivalents.
- **Exclude:** Bare numbers with currency inferred only from distant context,
  account numbers, prices without explicit currency, and generic `rupees` alone.
- **Boundaries:** Include currency, sign if present, amount, decimal/grouping
  punctuation, and scale words such as lakh, crore, million, or billion.
  Exclude approximation words (`about`) and surrounding prepositions.
- **Examples:** `The fictional [Lahore](CITY) fee is [PKR 5,000](MONEY).`;
  `The fictional [Karachi](CITY) budget is [Rs. 2.5 crore](MONEY).`
- **Paired range examples:** `The fictional fee is [PKR 500-700](MONEY).`;
  `The fictional fee ranges from [PKR 500](MONEY) to [PKR 700](MONEY).`
  In the second example, `from` and `to` stay O.
- **Ambiguity:** `5,000 rupees` is one MONEY. `PKR 500-700` is one MONEY range;
  `PKR 500 to PKR 700` gives two MONEY spans with `to` as O. Do not convert
  currencies or normalize lakh/crore. Explicit foreign-currency amounts also fit.

## PERCENT

- **Qualifies:** A numeric or written quantity explicitly marked by `%`,
  `percent`, `per cent`, or an equivalent Urdu percentage word.
- **Exclude:** Bare fractions, ratios, scores, and numbers without a percentage
  marker. `percentage points` is excluded under this project's narrow policy.
- **Boundaries:** Include sign, value, decimal punctuation, and percentage
  marker; exclude `about`, `increase of`, and surrounding prose.
- **Examples:** `The fictional [Punjab](PROVINCE_REGION) survey reports [25%](PERCENT).`;
  `The fictional [Sindh](PROVINCE_REGION) rate is [7.5 percent](PERCENT).`
- **Paired range examples:** `The fictional rate is [5-10%](PERCENT).`;
  `The fictional rate ranges from [5%](PERCENT) to [10%](PERCENT).`
  In the second example, `from` and `to` stay O.
- **Ambiguity:** `5-10%` is one PERCENT range; `5% to 10%` gives two PERCENT
  spans separated by O. `50 percent of respondents` excludes `of respondents`.
  A mathematically equivalent fraction such as `one quarter` is O.

## PHONE_NUMBER

- **Qualifies:** Explicit phone contacts, including synthetic/masked contacts
  in example data. Project recognition conventions cover domestic mobiles
  (`03` plus nine digits), international mobiles (`+92` replacing initial `0`),
  and landlines with an explicit area code and phone context. This describes
  annotation shapes, not proof that a number exists or is assigned.
- **Exclude:** CNICs, account/order numbers, bare quantities, and a generic
  `phone number` phrase with no value. Do not infer a contact from digit count alone.
- **Boundaries:** Include leading `+`, country/area code, internal spaces,
  parentheses, and hyphens belonging to the contact. Exclude `Phone:`, `Tel:`,
  and surrounding sentence punctuation. A separately introduced extension
  (`ext. 123`) stays O under this policy. Separate listed contacts are separate spans.
- **Examples (synthetic placeholders only):**
  `[Lahore](CITY) demo contact: [03XX-0000000](PHONE_NUMBER).`;
  `[Karachi](CITY) demo contact: [+92 3XX 0000000](PHONE_NUMBER).`
  A masked landline illustration is `[(021) XXX XXXX](PHONE_NUMBER)`; preserve its complete
  contact span if explicitly presented as a synthetic phone placeholder.
- **Ambiguity:** Do not hard-code every landline length or assume every long
  number is a telephone. Short helpline/service codes need explicit phone
  context and human review. A contiguous masked placeholder can still be one
  PHONE_NUMBER even though it intentionally fails real-number syntax. Never
  introduce real people's numbers into examples or review notes.

- **Project decision:** Documentation examples use masked placeholders.
  TRAINING data uses generated random digits in the mobile shapes
  `03XX-XXXXXXX` or `+92 3XX XXXXXXX` (each X replaced by a digit), never real
  people's numbers. Generated values are synthetic, not verified contacts.

## ID_NUMBER

- **Qualifies:** CNIC-format identifiers only, as defined by the supplied
  competition brief: 13 digits grouped 5-7-1 with hyphens, or 13 unhyphenated
  digits with explicit ID/CNIC context. Shape does not establish authenticity.
  Synthetic masked equivalents are valid documentation examples.
- **Exclude:** Passport, student, and other non-CNIC document IDs; phone numbers,
  bank accounts, transaction/order numbers, generic `CNIC` without a value,
  and unexplained unhyphenated digit strings.
- **Boundaries:** Include the complete CNIC with internal hyphens or masking
  characters; exclude `CNIC:`, `ID:`, quotes, and trailing punctuation.
  Do not split the three CNIC groups into separate entities.
- **Examples (synthetic placeholders only):**
  `[Lahore](CITY) demo CNIC: [XXXXX-0000000-X](ID_NUMBER).`;
  `[Karachi](CITY) demo CNIC: [XXXXXXXXXXXXX](ID_NUMBER).`
- **Project decision:** Documentation examples use masked placeholders.
  TRAINING data uses generated random digits in the 5-7-1 CNIC shape
  (`XXXXX-XXXXXXX-X`, with each X replaced by a digit), never real people's
  numbers. Generated values are synthetic, not verified CNICs.
- **Ambiguity:** Unhyphenated 13-digit values require explicit ID/CNIC context;
  length alone is insufficient. Never link generated CNICs to real people,
  infer identity, or copy personal identifiers into examples.

## Human adjudication before real annotation

Review these project decisions against any supplied competition manual:

1. Geographic coverage: districts/divisions as PROVINCE_REGION; handling natural
   features and addresses outside the ontology; disputed place names as written.
2. Institution scope: hospital/research institute classification, court-building
   references, bar associations, mixed regulators/tribunals, political alliances,
   party wings, university departments, and public commercial companies.
3. Metonymy: country names remain COUNTRY except explicit playing-team contexts;
   institutional versus physical-site readings require context.
4. Numeric scope: relative dates, date/time ranges, exclusion of durations and
   vague times, explicit currency requirement, and percentage-point exclusion.
5. Identifier handling: ID_NUMBER is CNIC-only under the supplied competition
   brief; review masked contacts, extensions, and short service codes. The project
   decision is masked documentation examples versus generated random digits in
   correctly shaped training phone/CNIC values, never real people's numbers.
6. Corpus tokenization, nested-name precedence, and aliases with insufficient
   context. Record decisions consistently before expanding the dataset.

For unresolved cases, keep the original text and proposed span in a separate
review log using synthetic/redacted identifiers only. Do not add REVIEW or any
other label to the vocabulary. Resolve uncertain annotations before treating
records as approved training data. The current validator checks structure and
BIO consistency; it cannot enforce these semantic decisions or privacy rules.
