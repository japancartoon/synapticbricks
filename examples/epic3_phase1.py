"""
BrickLang EPIC 3 Phase 1: Text Processing + Data Transformation

Building 30 essential bricks:
- Text Processing (15)
- Data Transformation (15)
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from collections import Counter, defaultdict
from datetime import datetime
import hashlib

sys.path.insert(0, str(Path(__file__).parent))

from core import brick, BrickEngine

print("=" * 80)
print("BrickLang EPIC 3 Phase 1: Building 30 Essential Bricks")
print("=" * 80)

engine = BrickEngine(project_dir="epic3_bricks")

# ===== TEXT PROCESSING (15 BRICKS) =====
print("\n[1/2] Building Text Processing Bricks (15)...")

@brick("split_text", description="Split text by delimiter")
def split_text(text: str, delimiter: str = " ", max_splits: int = -1) -> List[str]:
    """Split text into parts."""
    return text.split(delimiter, max_splits) if max_splits >= 0 else text.split(delimiter)

split_text.add_test(
    inputs={"text": "hello world test", "delimiter": " "},
    expected_output=["hello", "world", "test"],
    label="split_test"
)
engine.register(split_text)

@brick("join_text", description="Join list of strings")
def join_text(parts: List[str], separator: str = " ") -> str:
    """Join strings with separator."""
    return separator.join(parts)

join_text.add_test(
    inputs={"parts": ["hello", "world"], "separator": " "},
    expected_output="hello world",
    label="join_test"
)
engine.register(join_text)

@brick("strip_text", description="Remove leading/trailing whitespace")
def strip_text(text: str, chars: Optional[str] = None) -> str:
    """Strip whitespace or specific characters."""
    return text.strip(chars)

strip_text.add_test(
    inputs={"text": "  hello  "},
    expected_output="hello",
    label="strip_test"
)
engine.register(strip_text)

@brick("replace_text", description="Replace text pattern")
def replace_text(text: str, old: str, new: str, count: int = -1) -> str:
    """Replace occurrences of old with new."""
    return text.replace(old, new, count) if count >= 0 else text.replace(old, new)

replace_text.add_test(
    inputs={"text": "hello world", "old": "world", "new": "python"},
    expected_output="hello python",
    label="replace_test"
)
engine.register(replace_text)

@brick("regex_match", description="Match text with regex pattern")
def regex_match(text: str, pattern: str) -> Optional[List[str]]:
    """Match regex pattern, return groups."""
    match = re.search(pattern, text)
    return list(match.groups()) if match else None

regex_match.add_test(
    inputs={"text": "Price: $42.50", "pattern": r"\$(\d+\.\d+)"},
    expected_output=["42.50"],
    label="regex_test"
)
engine.register(regex_match)

@brick("regex_find_all", description="Find all pattern matches")
def regex_find_all(text: str, pattern: str) -> List[str]:
    """Find all matches of pattern."""
    return re.findall(pattern, text)

regex_find_all.add_test(
    inputs={"text": "abc123def456", "pattern": r"\d+"},
    expected_output=["123", "456"],
    label="findall_test"
)
engine.register(regex_find_all)

@brick("text_contains", description="Check if text contains substring")
def text_contains(text: str, substring: str, case_sensitive: bool = True) -> bool:
    """Check if substring is in text."""
    if not case_sensitive:
        return substring.lower() in text.lower()
    return substring in text

text_contains.add_test(
    inputs={"text": "Hello World", "substring": "world", "case_sensitive": False},
    expected_output=True,
    label="contains_test"
)
engine.register(text_contains)

@brick("text_starts_with", description="Check if text starts with prefix")
def text_starts_with(text: str, prefix: str, case_sensitive: bool = True) -> bool:
    """Check if text starts with prefix."""
    if not case_sensitive:
        return text.lower().startswith(prefix.lower())
    return text.startswith(prefix)

text_starts_with.add_test(
    inputs={"text": "Hello World", "prefix": "hello", "case_sensitive": False},
    expected_output=True,
    label="startswith_test"
)
engine.register(text_starts_with)

@brick("text_ends_with", description="Check if text ends with suffix")
def text_ends_with(text: str, suffix: str, case_sensitive: bool = True) -> bool:
    """Check if text ends with suffix."""
    if not case_sensitive:
        return text.lower().endswith(suffix.lower())
    return text.endswith(suffix)

text_ends_with.add_test(
    inputs={"text": "test.txt", "suffix": ".txt"},
    expected_output=True,
    label="endswith_test"
)
engine.register(text_ends_with)

@brick("text_uppercase", description="Convert to uppercase")
def text_uppercase(text: str) -> str:
    """Convert text to uppercase."""
    return text.upper()

text_uppercase.add_test(
    inputs={"text": "hello"},
    expected_output="HELLO",
    label="upper_test"
)
engine.register(text_uppercase)

@brick("text_lowercase", description="Convert to lowercase")
def text_lowercase(text: str) -> str:
    """Convert text to lowercase."""
    return text.lower()

text_lowercase.add_test(
    inputs={"text": "HELLO"},
    expected_output="hello",
    label="lower_test"
)
engine.register(text_lowercase)

@brick("text_capitalize", description="Capitalize first letter")
def text_capitalize(text: str) -> str:
    """Capitalize first letter of each word."""
    return text.title()

text_capitalize.add_test(
    inputs={"text": "hello world"},
    expected_output="Hello World",
    label="title_test"
)
engine.register(text_capitalize)

@brick("text_count", description="Count substring occurrences")
def text_count(text: str, substring: str, case_sensitive: bool = True) -> int:
    """Count occurrences of substring."""
    if not case_sensitive:
        return text.lower().count(substring.lower())
    return text.count(substring)

text_count.add_test(
    inputs={"text": "hello hello world", "substring": "hello"},
    expected_output=2,
    label="count_test"
)
engine.register(text_count)

@brick("extract_numbers", description="Extract all numbers from text")
def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text."""
    matches = re.findall(r'-?\d+\.?\d*', text)
    return [float(m) for m in matches if m]

extract_numbers.add_test(
    inputs={"text": "I have 42 apples and 3.14 oranges"},
    expected_output=[42.0, 3.14],
    label="extract_nums_test"
)
engine.register(extract_numbers)

@brick("truncate_text", description="Truncate text to max length")
def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

truncate_text.add_test(
    inputs={"text": "This is a long text", "max_length": 10},
    expected_output="This is...",
    label="truncate_test"
)
engine.register(truncate_text)

print(f"  ✅ Text Processing: 15/15 bricks")

# ===== DATA TRANSFORMATION (15 BRICKS) =====
print("\n[2/2] Building Data Transformation Bricks (15)...")

@brick("filter_list", description="Filter list by condition")
def filter_list(items: List[Any], condition: Callable[[Any], bool]) -> List[Any]:
    """Filter items that match condition."""
    return [item for item in items if condition(item)]

filter_list.add_test(
    inputs={"items": [1, 2, 3, 4, 5], "condition": lambda x: x > 2},
    expected_output=[3, 4, 5],
    label="filter_test"
)
engine.register(filter_list)

@brick("map_list", description="Transform list items")
def map_list(items: List[Any], transform: Callable[[Any], Any]) -> List[Any]:
    """Apply transformation to each item."""
    return [transform(item) for item in items]

map_list.add_test(
    inputs={"items": [1, 2, 3], "transform": lambda x: x * 2},
    expected_output=[2, 4, 6],
    label="map_test"
)
engine.register(map_list)

@brick("reduce_list", description="Reduce list to single value")
def reduce_list(items: List[Any], reducer: Callable[[Any, Any], Any], initial: Any = None) -> Any:
    """Reduce list using reducer function."""
    from functools import reduce
    if initial is not None:
        return reduce(reducer, items, initial)
    return reduce(reducer, items)

reduce_list.add_test(
    inputs={"items": [1, 2, 3, 4], "reducer": lambda a, b: a + b},
    expected_output=10,
    label="reduce_test"
)
engine.register(reduce_list)

@brick("sort_list", description="Sort list")
def sort_list(items: List[Any], key: Optional[Callable] = None, reverse: bool = False) -> List[Any]:
    """Sort list with optional key function."""
    return sorted(items, key=key, reverse=reverse)

sort_list.add_test(
    inputs={"items": [3, 1, 4, 1, 5], "reverse": False},
    expected_output=[1, 1, 3, 4, 5],
    label="sort_test"
)
engine.register(sort_list)

@brick("unique_items", description="Get unique items from list")
def unique_items(items: List[Any], preserve_order: bool = True) -> List[Any]:
    """Get unique items, optionally preserving order."""
    if preserve_order:
        seen = set()
        return [x for x in items if not (x in seen or seen.add(x))]
    return list(set(items))

unique_items.add_test(
    inputs={"items": [1, 2, 2, 3, 1, 4], "preserve_order": True},
    expected_output=[1, 2, 3, 4],
    label="unique_test"
)
engine.register(unique_items)

@brick("group_by", description="Group items by key")
def group_by(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """Group items by key value."""
    groups = defaultdict(list)
    for item in items:
        groups[item.get(key)].append(item)
    return dict(groups)

group_by.add_test(
    inputs={"items": [{"cat": "A", "val": 1}, {"cat": "B", "val": 2}, {"cat": "A", "val": 3}], "key": "cat"},
    expected_output={"A": [{"cat": "A", "val": 1}, {"cat": "A", "val": 3}], "B": [{"cat": "B", "val": 2}]},
    label="groupby_test"
)
engine.register(group_by)

@brick("count_items", description="Count item occurrences")
def count_items(items: List[Any]) -> Dict[Any, int]:
    """Count occurrences of each item."""
    return dict(Counter(items))

count_items.add_test(
    inputs={"items": ["a", "b", "a", "c", "b", "a"]},
    expected_output={"a": 3, "b": 2, "c": 1},
    label="count_test"
)
engine.register(count_items)

@brick("flatten_list", description="Flatten nested lists")
def flatten_list(items: List[Any], depth: int = 1) -> List[Any]:
    """Flatten nested lists to specified depth."""
    def flatten_once(lst):
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result
    
    result = items
    for _ in range(depth):
        result = flatten_once(result)
    return result

flatten_list.add_test(
    inputs={"items": [[1, 2], [3, 4], [5]], "depth": 1},
    expected_output=[1, 2, 3, 4, 5],
    label="flatten_test"
)
engine.register(flatten_list)

@brick("chunk_list", description="Split list into chunks")
def chunk_list(items: List[Any], size: int) -> List[List[Any]]:
    """Split list into chunks of size."""
    return [items[i:i + size] for i in range(0, len(items), size)]

chunk_list.add_test(
    inputs={"items": [1, 2, 3, 4, 5], "size": 2},
    expected_output=[[1, 2], [3, 4], [5]],
    label="chunk_test"
)
engine.register(chunk_list)

@brick("zip_lists", description="Zip multiple lists together")
def zip_lists(list1: List[Any], list2: List[Any]) -> List[tuple]:
    """Zip two lists into tuples."""
    return list(zip(list1, list2))

zip_lists.add_test(
    inputs={"list1": [1, 2, 3], "list2": ["a", "b", "c"]},
    expected_output=[(1, "a"), (2, "b"), (3, "c")],
    label="zip_test"
)
engine.register(zip_lists)

@brick("pluck_field", description="Extract field from list of dicts")
def pluck_field(items: List[Dict], field: str) -> List[Any]:
    """Extract specific field from all items."""
    return [item.get(field) for item in items]

pluck_field.add_test(
    inputs={"items": [{"name": "a", "value": 1}, {"name": "b", "value": 2}], "field": "name"},
    expected_output=["a", "b"],
    label="pluck_test"
)
engine.register(pluck_field)

@brick("merge_dicts", description="Merge multiple dictionaries")
def merge_dicts(dict1: Dict, dict2: Dict, dict3: Optional[Dict] = None) -> Dict:
    """Merge dictionaries (later values override)."""
    result = {}
    result.update(dict1)
    result.update(dict2)
    if dict3:
        result.update(dict3)
    return result

merge_dicts.add_test(
    inputs={"dict1": {"a": 1}, "dict2": {"b": 2}, "dict3": {"a": 3}},
    expected_output={"a": 3, "b": 2},
    label="merge_test"
)
engine.register(merge_dicts)

@brick("pick_keys", description="Pick specific keys from dict")
def pick_keys(data: Dict, keys: List[str]) -> Dict:
    """Pick only specified keys from dict."""
    return {k: data[k] for k in keys if k in data}

pick_keys.add_test(
    inputs={"data": {"a": 1, "b": 2, "c": 3}, "keys": ["a", "c"]},
    expected_output={"a": 1, "c": 3},
    label="pick_test"
)
engine.register(pick_keys)

@brick("omit_keys", description="Omit specific keys from dict")
def omit_keys(data: Dict, keys: List[str]) -> Dict:
    """Omit specified keys from dict."""
    return {k: v for k, v in data.items() if k not in keys}

omit_keys.add_test(
    inputs={"data": {"a": 1, "b": 2, "c": 3}, "keys": ["b"]},
    expected_output={"a": 1, "c": 3},
    label="omit_test"
)
engine.register(omit_keys)

@brick("invert_dict", description="Invert dictionary keys and values")
def invert_dict(data: Dict) -> Dict:
    """Swap keys and values in dictionary."""
    return {v: k for k, v in data.items()}

invert_dict.add_test(
    inputs={"data": {"a": 1, "b": 2}},
    expected_output={1: "a", 2: "b"},
    label="invert_test"
)
engine.register(invert_dict)

print(f"  ✅ Data Transformation: 15/15 bricks")

# ===== SUMMARY =====
print("\n" + "=" * 80)
print("EPIC 3 PHASE 1 COMPLETE!")
print("=" * 80)
print(f"\n✅ Total bricks built: {len(engine.bricks)}")
print(f"✅ Text Processing: 15 bricks")
print(f"✅ Data Transformation: 15 bricks")
print(f"\nNow you have 50 core bricks total! (20 + 30)")
print("\nNext: Test all 30 new bricks!")
print("=" * 80)
