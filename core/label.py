"""
BrickLabel — Compact labeling system for bricks.

Format: {category_code}{sequence_number}-{usage_count}
Examples:
  f54-13   → Function #54, used 13 times
  v12-3    → Validator #12, used 3 times
  d07-1    → Data transform #7, used once
  io03-5   → IO operation #3, used 5 times

Categories:
  f   = Pure function / computation
  v   = Validation / checks
  d   = Data transformation
  io  = Input/Output operations
  fmt = Formatting / display
  net = Network / API calls
  db  = Database operations
  auth = Authentication
  ctl = Control flow / routing
  err = Error handling
  cfg = Configuration
  utl = Utility / helper
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
import re


# Predefined categories with descriptions
BRICK_CATEGORIES = {
    "f":    {"name": "Function",       "desc": "Pure computation / logic"},
    "v":    {"name": "Validator",      "desc": "Input validation / checks"},
    "d":    {"name": "Data",           "desc": "Data transformation / mapping"},
    "io":   {"name": "IO",             "desc": "File / stream I/O operations"},
    "fmt":  {"name": "Format",         "desc": "Output formatting / display"},
    "net":  {"name": "Network",        "desc": "HTTP / API / socket calls"},
    "db":   {"name": "Database",       "desc": "Database read/write operations"},
    "auth": {"name": "Auth",           "desc": "Authentication / authorization"},
    "ctl":  {"name": "Control",        "desc": "Control flow / routing / branching"},
    "err":  {"name": "Error",          "desc": "Error handling / recovery"},
    "cfg":  {"name": "Config",         "desc": "Configuration loading / parsing"},
    "utl":  {"name": "Utility",        "desc": "General-purpose helpers"},
    "sec":  {"name": "Security",       "desc": "Encryption / hashing / sanitization"},
    "log":  {"name": "Logging",        "desc": "Logging / metrics / telemetry"},
    "cache": {"name": "Cache",         "desc": "Caching / memoization"},
    "parse": {"name": "Parser",        "desc": "Parsing structured data (JSON, CSV, XML)"},
    "math": {"name": "Math",           "desc": "Mathematical operations"},
    "str":  {"name": "String",         "desc": "String manipulation"},
    "arr":  {"name": "Array",          "desc": "List / array operations"},
    "async": {"name": "Async",         "desc": "Async / concurrent operations"},
}

# Label pattern: category_code + sequence_number + dash + usage_count
# e.g., f54-13, io03-5, parse12-1
LABEL_PATTERN = re.compile(r'^([a-z]+)(\d+)-(\d+)$')


@dataclass
class BrickLabel:
    """
    A brick's compact label.

    Attributes:
        category: Category code (e.g., 'f', 'v', 'io', 'parse')
        sequence: Unique number within category (auto-assigned)
        usage_count: How many places this brick is used
    """
    category: str
    sequence: int
    usage_count: int = 1

    @property
    def code(self) -> str:
        """Short code without usage: e.g., 'f54'"""
        return f"{self.category}{self.sequence:02d}"

    @property
    def full(self) -> str:
        """Full label with usage: e.g., 'f54-13'"""
        return f"{self.code}-{self.usage_count}"

    @property
    def category_name(self) -> str:
        """Human-readable category name."""
        cat = BRICK_CATEGORIES.get(self.category, {})
        return cat.get("name", self.category.upper())

    @property
    def category_desc(self) -> str:
        """Category description."""
        cat = BRICK_CATEGORIES.get(self.category, {})
        return cat.get("desc", "Unknown category")

    def increment_usage(self) -> None:
        """Called when this brick is used in a new place."""
        self.usage_count += 1

    def decrement_usage(self) -> None:
        """Called when a usage of this brick is removed."""
        self.usage_count = max(0, self.usage_count - 1)

    @staticmethod
    def parse(label_str: str) -> Optional["BrickLabel"]:
        """Parse a label string like 'f54-13' into a BrickLabel."""
        match = LABEL_PATTERN.match(label_str)
        if not match:
            return None
        category = match.group(1)
        sequence = int(match.group(2))
        usage = int(match.group(3))
        return BrickLabel(category=category, sequence=sequence, usage_count=usage)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "sequence": self.sequence,
            "usage_count": self.usage_count,
            "code": self.code,
            "full": self.full,
            "category_name": self.category_name,
        }

    def __repr__(self):
        return f"[{self.full}]"


class LabelRegistry:
    """
    Manages label assignment for all bricks.
    Auto-assigns sequence numbers within each category.
    Tracks usage counts across pipelines.
    """

    def __init__(self):
        # category -> next sequence number
        self._counters: Dict[str, int] = {}
        # brick_id -> BrickLabel
        self._labels: Dict[str, BrickLabel] = {}
        # label_code (e.g., 'f54') -> brick_id (reverse lookup)
        self._code_to_id: Dict[str, str] = {}

    def assign(self, brick_id: str, category: str) -> BrickLabel:
        """
        Assign a label to a brick.
        Auto-increments the sequence within the category.
        """
        if category not in BRICK_CATEGORIES:
            # Allow custom categories, just warn
            pass

        if brick_id in self._labels:
            return self._labels[brick_id]

        # Get next sequence number for this category
        seq = self._counters.get(category, 0) + 1
        self._counters[category] = seq

        label = BrickLabel(category=category, sequence=seq, usage_count=1)
        self._labels[brick_id] = label
        self._code_to_id[label.code] = brick_id

        return label

    def get_label(self, brick_id: str) -> Optional[BrickLabel]:
        """Get the label for a brick."""
        return self._labels.get(brick_id)

    def get_brick_id(self, label_code: str) -> Optional[str]:
        """Reverse lookup: label code (e.g., 'f54') -> brick_id."""
        # Handle full label (f54-13) by stripping usage count
        if '-' in label_code:
            label_code = label_code.split('-')[0]
        return self._code_to_id.get(label_code)

    def record_usage(self, brick_id: str) -> None:
        """Increment usage count when brick is used in a new pipeline step."""
        label = self._labels.get(brick_id)
        if label:
            label.increment_usage()

    def remove_usage(self, brick_id: str) -> None:
        """Decrement usage count when a pipeline step is removed."""
        label = self._labels.get(brick_id)
        if label:
            label.decrement_usage()

    def get_all_labels(self) -> Dict[str, BrickLabel]:
        """Get all assigned labels."""
        return dict(self._labels)

    def get_by_category(self, category: str) -> List[Dict[str, str]]:
        """Get all bricks in a specific category."""
        result = []
        for brick_id, label in self._labels.items():
            if label.category == category:
                result.append({
                    "brick_id": brick_id,
                    "label": label.full,
                    "code": label.code,
                    "usage": label.usage_count,
                })
        return result

    def summary(self) -> Dict[str, any]:
        """Category-level summary."""
        cats = {}
        for brick_id, label in self._labels.items():
            cat = label.category
            if cat not in cats:
                cats[cat] = {"count": 0, "total_usage": 0, "bricks": []}
            cats[cat]["count"] += 1
            cats[cat]["total_usage"] += label.usage_count
            cats[cat]["bricks"].append(label.full)

        return {
            "total_labels": len(self._labels),
            "categories_used": len(cats),
            "categories": cats,
        }

    def generate_code_map(self) -> str:
        """
        Generate a compact code map that an AI can read.
        This is the 'dictionary' the AI uses to understand the codebase.

        Example output:
          parse01-1  parse_input       Parser: Parse raw CSV line into dict
          v01-3      validate          Validator: Ensure data meets business rules
          f01-13     compute_grade     Function: Calculate letter grade
          fmt01-1    format_output     Format: Create human-readable output
        """
        lines = ["# BRICK CODE MAP", "# label      brick_id           category: description", ""]
        for brick_id, label in sorted(self._labels.items(), key=lambda x: x[1].code):
            cat_name = label.category_name
            lines.append(f"  {label.full:<12} {brick_id:<22} {cat_name}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "counters": dict(self._counters),
            "labels": {bid: l.to_dict() for bid, l in self._labels.items()},
        }
