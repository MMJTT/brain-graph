"""Core Brain Graph note and path mappings."""

NOTE_TYPE_PAPER = "paper"
NOTE_TYPE_CONCEPT = "concept"
NOTE_TYPE_METHOD = "method"
NOTE_TYPE_GAP = "gap"
NOTE_TYPE_AUTHOR = "author"
NOTE_TYPE_MAP = "map"

NOTE_TYPES = (
    NOTE_TYPE_PAPER,
    NOTE_TYPE_CONCEPT,
    NOTE_TYPE_METHOD,
    NOTE_TYPE_GAP,
    NOTE_TYPE_AUTHOR,
    NOTE_TYPE_MAP,
)

RAW_KIND_PAPER = "paper"
RAW_KIND_CLIP = "clip"
RAW_KIND_METADATA = "metadata"

RAW_KINDS = (
    RAW_KIND_PAPER,
    RAW_KIND_CLIP,
    RAW_KIND_METADATA,
)

COMPILER_BACKEND_HEURISTIC = "heuristic"
COMPILER_BACKEND_OPENROUTER = "openrouter"

COMPILER_BACKENDS = (
    COMPILER_BACKEND_HEURISTIC,
    COMPILER_BACKEND_OPENROUTER,
)

DISCOVERY_PROVIDER_ARXIV = "arxiv"
DISCOVERY_PROVIDER_SEMANTIC_SCHOLAR = "semantic-scholar"
DISCOVERY_PROVIDER_BOTH = "both"

DISCOVERY_PROVIDERS = (
    DISCOVERY_PROVIDER_ARXIV,
    DISCOVERY_PROVIDER_SEMANTIC_SCHOLAR,
    DISCOVERY_PROVIDER_BOTH,
)

COMPILE_STATUS_IMPORTED = "imported"
COMPILE_STATUS_COMPILED = "compiled"
COMPILE_STATUS_FAILED = "failed"

WIKI_DIRECTORY_BY_NOTE_TYPE = {
    NOTE_TYPE_PAPER: "papers",
    NOTE_TYPE_CONCEPT: "concepts",
    NOTE_TYPE_METHOD: "methods",
    NOTE_TYPE_GAP: "gaps",
    NOTE_TYPE_AUTHOR: "authors",
    NOTE_TYPE_MAP: "maps",
}

NOTE_TYPE_BY_WIKI_DIRECTORY = {
    directory: note_type for note_type, directory in WIKI_DIRECTORY_BY_NOTE_TYPE.items()
}

RAW_DIRECTORY_BY_KIND = {
    RAW_KIND_PAPER: "papers",
    RAW_KIND_CLIP: "clips",
    RAW_KIND_METADATA: "metadata",
}

TEMPLATE_FIELDS_BY_NOTE_TYPE = {
    NOTE_TYPE_PAPER: (
        "id",
        "title",
        "node_type",
        "status",
        "tags",
        "created",
        "updated",
        "source_refs",
        "related",
        "year",
        "venue",
        "authors",
        "paper_url",
        "raw_refs",
        "concept_refs",
        "method_refs",
        "gap_refs",
    ),
    NOTE_TYPE_CONCEPT: (
        "id",
        "title",
        "node_type",
        "status",
        "tags",
        "created",
        "updated",
        "source_refs",
        "related",
        "aliases",
        "parent_concepts",
        "paper_refs",
        "method_refs",
    ),
    NOTE_TYPE_METHOD: (
        "id",
        "title",
        "node_type",
        "status",
        "tags",
        "created",
        "updated",
        "source_refs",
        "related",
        "introduced_by",
        "applies_to",
        "limitations",
    ),
    NOTE_TYPE_GAP: (
        "id",
        "title",
        "node_type",
        "status",
        "tags",
        "created",
        "updated",
        "source_refs",
        "related",
        "gap_kind",
        "raised_by",
        "potential_directions",
    ),
    NOTE_TYPE_AUTHOR: (
        "id",
        "title",
        "node_type",
        "status",
        "tags",
        "created",
        "updated",
        "source_refs",
        "related",
        "affiliation",
        "paper_refs",
    ),
    NOTE_TYPE_MAP: (
        "id",
        "title",
        "node_type",
        "status",
        "tags",
        "created",
        "updated",
        "source_refs",
        "related",
        "focus",
        "includes",
        "questions",
    ),
}
