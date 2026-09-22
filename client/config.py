"""Per-client search configuration - Carolina (bioengineer, PhD in
tissue engineering and mechanobiology, GMP exposure; RAV Graubünden).

Built 2026-09-22 from the intake form and CV. Private data (salary floors,
contact details, insured salary) is NOT here: it lives in the
CANDIDATE_PROFILE secret and the private Claude Project.

Applies only in English. Ads in German are searched (most Swiss
life-science ads are), but the scoring profile handles the language rule.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Geography - four relocation tiers from the intake form
# ---------------------------------------------------------------------------
HOME_REGION = "Basel region"

TIER_LABELS = {1: "Basel region", 2: "Zurich region",
               3: "Lake Geneva / rest of CH / remote",
               4: "NL / BE / DK / DE / AT", 0: "Out of area"}

# Evaluated in order against "<location> <title>"; first match wins.
TIER_PATTERNS = [
    # Basel-Stadt, Basel-Land, the Fricktal, Solothurn's pharma belt,
    # and the immediate cross-border ring (Lörrach, Saint-Louis, Grenzach).
    (1, re.compile(r"\b(BS|BL|Basel|Bâle|Allschwil|Kaiseraugst|Muttenz"
                   r"|Pratteln|Reinach|Aesch|Liestal|Sissach|Stein|Rheinfelden"
                   r"|Frick|Möhlin|Moehlin|Schweizerhalle|Grenzach|L[öo]rrach"
                   r"|Saint-Louis|Weil am Rhein|Solothurn|Olten|Balsthal"
                   r"|Dornach)\b", re.I)),
    (2, re.compile(r"\b(ZH|Z[uü]rich|Zurich|Zurigo|Schlieren|Winterthur"
                   r"|Wädenswil|Waedenswil|Zug|ZG|Baar|Rotkreuz|Dübendorf"
                   r"|Duebendorf|Kloten|Opfikon|Wallisellen|Regensdorf"
                   r"|Bülach|Baden|Lengnau)\b", re.I)),
    (3, re.compile(r"\b(Switzerland|Schweiz|Suisse|Svizzera|CH|Lausanne"
                   r"|Gen[eè]ve|Geneva|Genf|Epalinges|Vaud|VD|GE|Nyon|Morges"
                   r"|Vevey|Montreux|Bern|Berne|Biel|Bienne|Neuch[aâ]tel"
                   r"|Marin|Luzern|Lucerne|Visp|Monthey|Valais|Wallis|Sion"
                   r"|St\.? ?Gallen|SG|Fribourg|Freiburg \(CH\)|Chur|Davos"
                   r"|Lugano|Ticino|Tessin|Schaffhausen|Thun|Burgdorf"
                   r"|Bubendorf|Lenzburg|Aarau|Aargau|remote|home ?office"
                   r"|hybrid)\b", re.I)),
    (4, re.compile(r"\b(Netherlands|Nederland|Holland|Leiden|Amsterdam"
                   r"|Utrecht|Eindhoven|Rotterdam|Groningen|Maastricht"
                   r"|Nijmegen|Wageningen|Delft|Belgium|Belgi[eë]|Belgique"
                   r"|Leuven|Louvain|Ghent|Gent|Brussels|Bruxelles|Antwerp"
                   r"|Antwerpen|Li[eè]ge|Denmark|Danmark|Copenhagen"
                   r"|K[øo]benhavn|Aarhus|Odense|Lyngby|Germany|Deutschland"
                   r"|Berlin|M[uü]nchen|Munich|Hamburg|Frankfurt|Heidelberg"
                   r"|Mannheim|T[uü]bingen|Reutlingen|Stuttgart|Freiburg"
                   r"|Ulm|Biberach|Ingelheim|Mainz|Marburg|Melsungen"
                   r"|Leipzig|Dresden|Aachen|K[öo]ln|Cologne|D[üu]sseldorf"
                   r"|Hannover|G[öo]ttingen|W[üu]rzburg|Regensburg|Penzberg"
                   r"|Martinsried|Planegg|Austria|[ÖO]sterreich|Wien|Vienna"
                   r"|Graz|Innsbruck|Linz|Salzburg|Krems)\b", re.I)),
]

REGION_SOURCES: set[str] = set()

# ---------------------------------------------------------------------------
# Title gate - the intake form's "titles you want" + "would consider"
# ---------------------------------------------------------------------------
TITLE_PASS = re.compile(
    r"(scientist|wissenschaftler|researcher|research (associate|engineer"
    r"|fellow|specialist|technologist)|postdoc|post-doc|bioengineer"
    r"|bio-engineer|biomedical engineer|biotechnolog|tissue engineer"
    r"|cell (culture|therapy|biolog)|stem cell|biomaterial|hydrogel"
    r"|process (engineer|expert|specialist|scientist|developer"
    r"|development)|manufacturing (specialist|associate|scientist"
    r"|engineer|expert|technologist|process)|msat|ms&t|manufacturing science"
    r"|technology transfer|tech transfer|product engineer|project manager"
    r"|projektleiter|projektmanager|r&d engineer|r&d specialist"
    r"|development (scientist|engineer|associate)|laboratory (scientist"
    r"|specialist|manager)|lab (scientist|specialist|manager)"
    r"|medical science liaison|msl\b|scientific writer|medical writer"
    r"|science writer|application (scientist|specialist|engineer)"
    r"|field application|regulatory affairs|regulatory (specialist"
    r"|associate|manager)|quality (assurance|control|specialist|associate"
    r"|engineer)|qa (specialist|associate|manager|engineer)|qc (specialist"
    r"|associate|analyst|scientist)|validation (engineer|specialist)"
    r"|data (analyst|scientist)|consultant|histolog|imaging (specialist"
    r"|scientist)|microscop|bioprocess|gmp|upstream|downstream)", re.I)

TITLE_BLOCK = re.compile(
    r"\b(intern(ship)?|praktik(um|ant|antin)|lehrstelle|lehrling|apprentice"
    r"|trainee|werkstudent|student(in)?|bachelor|master thesis|masterarbeit"
    r"|thesis|phd (position|student|candidate)|doktorand|doctoral"
    r"|director|vice president|vp\b|chief|head of|leiter(in)? (der|des)"
    r"|professor|professur|nurse|pflege|physician|arzt|ärztin|pharmacist"
    r"|apotheker|sales (rep|representative|manager)|account manager"
    r"|business development|group leader|principal|laborant(in)?"
    r"|reinigung|cleaner|driver|cook|server|cashier)\b", re.I)

# Distinct flags, not buried: academic and contract routes back into the
# lab, plus the interim/temporary seats recruiters fill fast.
WILDCARD = re.compile(r"\b(postdoc|post-doc|fellow(ship)?|temporary|befristet"
                      r"|temporär|contract|interim|start-?up|scale-?up"
                      r"|medical writer|scientific writer|consultant)\b", re.I)

# ---------------------------------------------------------------------------
# Job-Room (arbeit.swiss) - source #1. Cantons empty: she relocates
# anywhere in Switzerland. English and German keywords: most Swiss
# life-science ads are German even when the working language is English.
# ---------------------------------------------------------------------------
JOBROOM_KEYWORDS = [
    "scientist", "bioengineer", "biomedical engineer", "tissue engineering",
    "cell culture", "GMP", "process engineer", "research associate",
    "manufacturing specialist", "MSAT", "regulatory affairs",
    "quality control", "application scientist", "postdoc",
    "Wissenschaftler", "Zellkultur", "Prozessingenieur", "Biotechnologe",
]
JOBROOM_CANTONS: list[str] = []      # all of Switzerland
JOBROOM_WORKLOAD_MIN = 80

# ---------------------------------------------------------------------------
# LinkedIn
# ---------------------------------------------------------------------------
_CORE = ("scientist OR bioengineer OR \"research associate\" "
         "OR \"tissue engineering\" OR \"cell culture\"")
_PROCESS = ("\"process engineer\" OR \"manufacturing specialist\" OR MSAT "
            "OR GMP OR \"cell therapy\"")

LINKEDIN_GUEST_SEARCHES = [
    (_CORE, "Basel, Switzerland", None),
    (_PROCESS, "Basel, Switzerland", None),
    (_CORE, "Zurich, Switzerland", None),
    (_CORE + " OR " + _PROCESS, "Switzerland", None),
    ("\"tissue engineering\" OR \"cell therapy\" OR bioengineer scientist",
     "Netherlands", None),
    ("\"tissue engineering\" OR \"cell therapy\" OR bioengineer scientist",
     "Germany", None),
]

LINKEDIN_AUTH_SEARCHES = [
    (_CORE, "Basel, Switzerland", False),
    (_PROCESS, "Basel, Switzerland", False),
    (_CORE, "Zurich, Switzerland", False),
    (_CORE + " OR " + _PROCESS, "Switzerland", False),
    ("\"tissue engineering\" OR \"cell therapy\" OR bioengineer scientist",
     "Netherlands", False),
    ("\"tissue engineering\" OR \"cell therapy\" OR bioengineer scientist",
     "Germany", False),
]

# ---------------------------------------------------------------------------
# Adzuna (optional). Swiss index first; de/nl/at cover tier 4.
# ---------------------------------------------------------------------------
_ADZ = ("scientist bioengineer \"research associate\" \"process engineer\" "
        "\"tissue engineering\" \"cell culture\" GMP MSAT")
ADZUNA_QUERIES = [
    ("ch", {"what_or": _ADZ, "where": "Basel", "distance": 40}),
    ("ch", {"what_or": _ADZ, "where": "Zurich", "distance": 40}),
    ("ch", {"what_or": _ADZ}),
    ("de", {"what_or": "\"tissue engineering\" \"cell therapy\" bioengineer "
                       "\"biomedical engineer\" scientist GMP"}),
    ("nl", {"what_or": "\"tissue engineering\" \"cell therapy\" bioengineer "
                       "\"biomedical engineer\" scientist GMP"}),
    ("at", {"what_or": "\"tissue engineering\" \"cell therapy\" bioengineer "
                       "scientist GMP"}),
]

# ---------------------------------------------------------------------------
# Recruiters - Swiss life-science specialists (researched 2026-09-22)
# ---------------------------------------------------------------------------
# Proclinical's Swiss listing page serves plain HTML job links (verified);
# the others render client-side and sit in the watch panel only.
RECRUITER_SCRAPED_FIRMS = [
    ("Proclinical", "https://www.proclinical.com/switzerland-life-science-jobs",
     "Switzerland", 0),
]

RECRUITER_TITLE = re.compile(
    r"\b(scientist|engineer|associate|specialist|bioengineer|research"
    r"|manufacturing|process|msat|gmp|quality|qa|qc|regulatory|validation"
    r"|cell|tissue|biolog|laborator|lab|application|liaison|writer"
    r"|technologist|analyst)\b", re.I)

RECRUITER_WATCH = [
    ("Coopers Group", "Basel · life sciences, temp + permanent",
     "https://www.coopers.ch/en/jobs/"),
    ("CTC Resourcing Solutions", "Basel · pharma, biotech, medtech, CRO",
     "https://www.ctcresourcing.com/jobs/"),
    ("Proclinical", "Basel · biopharma and medtech, contract + permanent",
     "https://www.proclinical.com/switzerland-life-science-jobs"),
    ("R&D Partners", "Basel · drug development and manufacturing",
     "https://www.r-dpartners.com/jobs/"),
    ("headcount AG", "Zürich · pharma, biotech, medical devices",
     "https://headcount.ch/"),
    ("Hays Life Sciences", "Switzerland · pharma, biotech, medtech",
     "https://www.hays.ch/en/applicants/areas-of-expertise/life-sciences"),
    ("Michael Page Healthcare & Life Sciences", "Switzerland · permanent + interim",
     "https://www.michaelpage.ch/jobs/healthcare-life-sciences"),
    ("Swisslinx Life Sciences", "Basel / Zürich · pharma, biotech, start-ups",
     "https://www.swisslinx.com/healthcare-life-sciences"),
    ("Randstad Life Sciences", "Switzerland · lab and production seats",
     "https://www.randstad.ch/en/jobs/q-life-sciences/"),
    ("Kelly Life Sciences", "Switzerland · Gi Group, scientist recruiters",
     "https://www.kellyservices.ch/disciplines/life-sciences"),
    ("NonStop Consulting", "Zürich · European life-science network",
     "https://nonstopconsulting.com/our-services/life-sciences/"),
]
RECRUITER_WATCH_TITLE = "Recruiter watch — Swiss life sciences"
RECRUITER_WATCH_BLURB = ("Lab, process and scientist postings from this firm "
                         "appear in the job sections automatically when they "
                         "match.")

# ---------------------------------------------------------------------------
# Reading - where biotech, regenerative medicine and AI intersect.
# All feeds verified reachable 2026-09-22.
# ---------------------------------------------------------------------------
AI_FEEDS = [
    ("Fierce Biotech · AI", "https://www.fiercebiotech.com/rss/xml?tag=ai"),
    ("Labiotech.eu · AI", "https://www.labiotech.eu/tag/artificial-intelligence/feed/"),
    ("STAT · Health Tech", "https://www.statnews.com/category/health-tech/feed/"),
    ("MIT Technology Review · Biotechnology",
     "https://www.technologyreview.com/topic/biotechnology/feed"),
    ("Nature Biotechnology", "https://www.nature.com/nbt.rss"),
    ("RegMedNet", "https://www.regmednet.com/feed/"),
]

REGIONAL_BUSINESS_FEEDS = [
    ("Startupticker.ch", "https://www.startupticker.ch/en/rss/news"),
    ("Swiss Biotech Association", "https://www.swissbiotech.org/feed/"),
    ("Basel Area Business & Innovation", "https://www.baselarea.swiss/feed/"),
    ("Labiotech.eu", "https://www.labiotech.eu/feed/"),
]

# ---------------------------------------------------------------------------
# Interview brief
# ---------------------------------------------------------------------------
INTERVIEW_BRIEF_PERSONA = (
    "a bioengineer finishing a PhD in tissue engineering and mechanobiology "
    "(GMP-adjacent manufacturing exposure, 3D cell culture, biomaterials, "
    "advanced imaging) interviewing for R&D scientist, process and "
    "manufacturing, MSAT and application-scientist seats at Swiss and "
    "European life-science companies")
INTERVIEW_BRIEF_DEFAULT_ROLE = "R&D or process scientist role"
