"""
models/enums.py
===============
Canonical enumerations used throughout the workflow.
Centralised here so no string is ever hard-coded in multiple places.
"""
from enum import Enum


class RoutingState(str, Enum):
    READY_FOR_REVIEW       = "READY_FOR_REVIEW"
    NEED_INFO              = "NEED_INFO"
    URGENT_REVIEW          = "URGENT_REVIEW"
    PRIORITY_REVIEW        = "PRIORITY_REVIEW"
    OTHER_SUPPORT          = "OTHER_SUPPORT"
    NO_ACTION_RECOMMENDED  = "NO_ACTION_RECOMMENDED"
    REFERRED               = "REFERRED"
    HUMAN_OVERRIDE         = "HUMAN_OVERRIDE"


class SeverityLevel(str, Enum):
    NONE     = "NONE"
    LOW      = "LOW"
    MODERATE = "MODERATE"
    HIGH     = "HIGH"
    URGENT   = "URGENT"


class IndicatorSource(str, Enum):
    STRUCTURED_FIELD      = "structured_field"
    NARRATIVE_EXTRACTION  = "narrative_extraction"
    LLM_EXTRACTED         = "llm_extracted"


class IndicatorConfidence(str, Enum):
    REPORTED  = "REPORTED"
    POSSIBLE  = "POSSIBLE"
    INFERRED  = "INFERRED"


class DecisionSource(str, Enum):
    DETERMINISTIC = "deterministic"
    LLM_ASSISTED  = "llm_assisted"
    HUMAN         = "human"


class HITLDecision(str, Enum):
    APPROVED   = "APPROVED"
    EDITED     = "EDITED"
    ESCALATED  = "ESCALATED"
    DOWNGRADED = "DOWNGRADED"
    MORE_INFO  = "MORE_INFO"


ROUTING_STATE_LABELS: dict[str, str] = {
    RoutingState.URGENT_REVIEW:        "Urgent Safeguarding Review",
    RoutingState.PRIORITY_REVIEW:      "Priority Review",
    RoutingState.READY_FOR_REVIEW:     "Ready for Review",
    RoutingState.NEED_INFO:            "More Information Required",
    RoutingState.OTHER_SUPPORT:        "Labour / Other Support",
    RoutingState.NO_ACTION_RECOMMENDED:"No Action Recommended",
    RoutingState.REFERRED:             "Referred",
    RoutingState.HUMAN_OVERRIDE:       "Human Override",
}
