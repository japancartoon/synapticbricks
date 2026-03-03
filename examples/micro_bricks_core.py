"""
BrickLang EPIC 2: Micro-Bricks (Assembly-Level Primitives)

These are the atoms of computation - the smallest possible operations.
Each maps directly to CPU instructions or bytecode.
"""

import sys
from pathlib import Path
from typing import Any, Optional, Callable
import ctypes

sys.path.insert(0, str(Path(__file__).parent))

from core import brick, BrickEngine

print("=" * 80)
print("BrickLang EPIC 2: Building 50 Micro-Bricks (Assembly-Level)")
print("=" * 80)

engine = BrickEngine(project_dir="micro_bricks")

# ===== MEMORY OPERATIONS (10) =====
print("\n[1/5] Building Memory Operations (10)...")

@brick("mem_alloc", description="[MICRO] Allocate memory block")
def mem_alloc(size: int) -> int:
    """Allocate memory, return address (simulated with id)."""
    obj = bytearray(size)
    return id(obj)

mem_alloc.add_test(
    inputs={"size": 1024},
    expected_output=lambda x: isinstance(x, int) and x > 0,
    label="mem_alloc_test"
)
engine.register(mem_alloc)

@brick("mem_load", description="[MICRO] Load value from address")
def mem_load(data: Any) -> Any:
    """Load value (in Python, just return it)."""
    return data

mem_load.add_test(
    inputs={"data": 42},
    expected_output=42,
    label="mem_load_test"
)
engine.register(mem_load)

@brick("mem_store", description="[MICRO] Store value to address")
def mem_store(address: dict, key: str, value: Any) -> bool:
    """Store value at address (simulated with dict)."""
    address[key] = value
    return True

mem_store.add_test(
    inputs={"address": {}, "key": "x", "value": 10},
    expected_output=True,
    label="mem_store_test"
)
engine.register(mem_store)

@brick("mem_copy", description="[MICRO] Copy memory region")
def mem_copy(source: bytes, start: int, length: int) -> bytes:
    """Copy bytes from source."""
    return source[start:start+length]

mem_copy.add_test(
    inputs={"source": b"Hello World", "start": 0, "length": 5},
    expected_output=b"Hello",
    label="mem_copy_test"
)
engine.register(mem_copy)

@brick("mem_set", description="[MICRO] Set memory to value")
def mem_set(size: int, value: int) -> bytes:
    """Create bytes filled with value."""
    return bytes([value % 256] * size)

mem_set.add_test(
    inputs={"size": 5, "value": 0},
    expected_output=b"\x00\x00\x00\x00\x00",
    label="mem_set_test"
)
engine.register(mem_set)

@brick("mem_compare", description="[MICRO] Compare memory regions")
def mem_compare(a: bytes, b: bytes) -> int:
    """Compare bytes, return -1/0/1."""
    if a < b: return -1
    if a > b: return 1
    return 0

mem_compare.add_test(
    inputs={"a": b"abc", "b": b"abc"},
    expected_output=0,
    label="mem_compare_test"
)
engine.register(mem_compare)

@brick("mem_size", description="[MICRO] Get object size")
def mem_size(obj: Any) -> int:
    """Get size of object."""
    if hasattr(obj, '__len__'):
        return len(obj)
    return 1

mem_size.add_test(
    inputs={"obj": [1, 2, 3]},
    expected_output=3,
    label="mem_size_test"
)
engine.register(mem_size)

@brick("stack_push", description="[MICRO] Push to stack")
def stack_push(stack: list, value: Any) -> bool:
    """Push value onto stack."""
    stack.append(value)
    return True

stack_push.add_test(
    inputs={"stack": [], "value": 42},
    expected_output=True,
    label="stack_push_test"
)
engine.register(stack_push)

@brick("stack_pop", description="[MICRO] Pop from stack")
def stack_pop(stack: list) -> Any:
    """Pop value from stack."""
    return stack.pop() if stack else None

stack_pop.add_test(
    inputs={"stack": [1, 2, 3]},
    expected_output=3,
    label="stack_pop_test"
)
engine.register(stack_pop)

@brick("stack_peek", description="[MICRO] Peek at stack top")
def stack_peek(stack: list) -> Any:
    """Peek at top of stack without removing."""
    return stack[-1] if stack else None

stack_peek.add_test(
    inputs={"stack": [1, 2, 3]},
    expected_output=3,
    label="stack_peek_test"
)
engine.register(stack_peek)

print(f"  ✅ Memory: 10/10 micro-bricks")

# ===== ARITHMETIC OPERATIONS (10) =====
print("\n[2/5] Building Arithmetic Operations (10)...")

@brick("add_int", description="[MICRO] Add two integers")
def add_int(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

add_int.add_test(
    inputs={"a": 5, "b": 3},
    expected_output=8,
    label="add_test"
)
engine.register(add_int)

@brick("sub_int", description="[MICRO] Subtract integers")
def sub_int(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b

sub_int.add_test(
    inputs={"a": 10, "b": 3},
    expected_output=7,
    label="sub_test"
)
engine.register(sub_int)

@brick("mul_int", description="[MICRO] Multiply integers")
def mul_int(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

mul_int.add_test(
    inputs={"a": 4, "b": 5},
    expected_output=20,
    label="mul_test"
)
engine.register(mul_int)

@brick("div_int", description="[MICRO] Divide integers")
def div_int(a: int, b: int) -> dict:
    """Divide a by b, return quotient and remainder."""
    return {"quotient": a // b, "remainder": a % b}

div_int.add_test(
    inputs={"a": 17, "b": 5},
    expected_output={"quotient": 3, "remainder": 2},
    label="div_test"
)
engine.register(div_int)

@brick("mod_int", description="[MICRO] Modulo operation")
def mod_int(a: int, b: int) -> int:
    """Return a modulo b."""
    return a % b

mod_int.add_test(
    inputs={"a": 17, "b": 5},
    expected_output=2,
    label="mod_test"
)
engine.register(mod_int)

@brick("neg_int", description="[MICRO] Negate integer")
def neg_int(a: int) -> int:
    """Negate integer."""
    return -a

neg_int.add_test(
    inputs={"a": 42},
    expected_output=-42,
    label="neg_test"
)
engine.register(neg_int)

@brick("abs_int", description="[MICRO] Absolute value")
def abs_int(a: int) -> int:
    """Absolute value."""
    return abs(a)

abs_int.add_test(
    inputs={"a": -42},
    expected_output=42,
    label="abs_test"
)
engine.register(abs_int)

@brick("min_int", description="[MICRO] Minimum of two")
def min_int(a: int, b: int) -> int:
    """Return minimum."""
    return a if a < b else b

min_int.add_test(
    inputs={"a": 5, "b": 3},
    expected_output=3,
    label="min_test"
)
engine.register(min_int)

@brick("max_int", description="[MICRO] Maximum of two")
def max_int(a: int, b: int) -> int:
    """Return maximum."""
    return a if a > b else b

max_int.add_test(
    inputs={"a": 5, "b": 3},
    expected_output=5,
    label="max_test"
)
engine.register(max_int)

@brick("inc_int", description="[MICRO] Increment by 1")
def inc_int(a: int) -> int:
    """Increment by 1."""
    return a + 1

inc_int.add_test(
    inputs={"a": 41},
    expected_output=42,
    label="inc_test"
)
engine.register(inc_int)

print(f"  ✅ Arithmetic: 10/10 micro-bricks")

# ===== LOGIC OPERATIONS (10) =====
print("\n[3/5] Building Logic Operations (10)...")

@brick("and_bits", description="[MICRO] Bitwise AND")
def and_bits(a: int, b: int) -> int:
    """Bitwise AND."""
    return a & b

and_bits.add_test(
    inputs={"a": 0b1100, "b": 0b1010},
    expected_output=0b1000,
    label="and_test"
)
engine.register(and_bits)

@brick("or_bits", description="[MICRO] Bitwise OR")
def or_bits(a: int, b: int) -> int:
    """Bitwise OR."""
    return a | b

or_bits.add_test(
    inputs={"a": 0b1100, "b": 0b1010},
    expected_output=0b1110,
    label="or_test"
)
engine.register(or_bits)

@brick("xor_bits", description="[MICRO] Bitwise XOR")
def xor_bits(a: int, b: int) -> int:
    """Bitwise XOR."""
    return a ^ b

xor_bits.add_test(
    inputs={"a": 0b1100, "b": 0b1010},
    expected_output=0b0110,
    label="xor_test"
)
engine.register(xor_bits)

@brick("not_bits", description="[MICRO] Bitwise NOT")
def not_bits(a: int, bits: int = 32) -> int:
    """Bitwise NOT (limited to bits)."""
    mask = (1 << bits) - 1
    return ~a & mask

not_bits.add_test(
    inputs={"a": 0b1100, "bits": 4},
    expected_output=0b0011,
    label="not_test"
)
engine.register(not_bits)

@brick("shift_left", description="[MICRO] Left shift")
def shift_left(a: int, n: int) -> int:
    """Left shift by n bits."""
    return a << n

shift_left.add_test(
    inputs={"a": 0b0001, "n": 3},
    expected_output=0b1000,
    label="shl_test"
)
engine.register(shift_left)

@brick("shift_right", description="[MICRO] Right shift")
def shift_right(a: int, n: int) -> int:
    """Right shift by n bits."""
    return a >> n

shift_right.add_test(
    inputs={"a": 0b1000, "n": 3},
    expected_output=0b0001,
    label="shr_test"
)
engine.register(shift_right)

@brick("rotate_left", description="[MICRO] Rotate left")
def rotate_left(a: int, n: int, bits: int = 32) -> int:
    """Rotate left by n bits."""
    n %= bits
    mask = (1 << bits) - 1
    a &= mask
    return ((a << n) | (a >> (bits - n))) & mask

rotate_left.add_test(
    inputs={"a": 0b1100, "n": 1, "bits": 4},
    expected_output=0b1001,
    label="rol_test"
)
engine.register(rotate_left)

@brick("rotate_right", description="[MICRO] Rotate right")
def rotate_right(a: int, n: int, bits: int = 32) -> int:
    """Rotate right by n bits."""
    n %= bits
    mask = (1 << bits) - 1
    a &= mask
    return ((a >> n) | (a << (bits - n))) & mask

rotate_right.add_test(
    inputs={"a": 0b1001, "n": 1, "bits": 4},
    expected_output=0b1100,
    label="ror_test"
)
engine.register(rotate_right)

@brick("count_bits", description="[MICRO] Count set bits")
def count_bits(a: int) -> int:
    """Count number of 1 bits."""
    return bin(a).count('1')

count_bits.add_test(
    inputs={"a": 0b1011},
    expected_output=3,
    label="popcount_test"
)
engine.register(count_bits)

@brick("test_bit", description="[MICRO] Test bit at position")
def test_bit(a: int, pos: int) -> bool:
    """Test if bit at position is set."""
    return bool((a >> pos) & 1)

test_bit.add_test(
    inputs={"a": 0b1010, "pos": 1},
    expected_output=True,
    label="test_bit_test"
)
engine.register(test_bit)

print(f"  ✅ Logic: 10/10 micro-bricks")

# ===== COMPARISON OPERATIONS (10) =====
print("\n[4/5] Building Comparison Operations (10)...")

@brick("compare_eq", description="[MICRO] Equal")
def compare_eq(a: Any, b: Any) -> bool:
    """Check equality."""
    return a == b

compare_eq.add_test(
    inputs={"a": 42, "b": 42},
    expected_output=True,
    label="eq_test"
)
engine.register(compare_eq)

@brick("compare_ne", description="[MICRO] Not equal")
def compare_ne(a: Any, b: Any) -> bool:
    """Check inequality."""
    return a != b

compare_ne.add_test(
    inputs={"a": 42, "b": 10},
    expected_output=True,
    label="ne_test"
)
engine.register(compare_ne)

@brick("compare_lt", description="[MICRO] Less than")
def compare_lt(a: Any, b: Any) -> bool:
    """Check less than."""
    return a < b

compare_lt.add_test(
    inputs={"a": 5, "b": 10},
    expected_output=True,
    label="lt_test"
)
engine.register(compare_lt)

@brick("compare_le", description="[MICRO] Less or equal")
def compare_le(a: Any, b: Any) -> bool:
    """Check less or equal."""
    return a <= b

compare_le.add_test(
    inputs={"a": 10, "b": 10},
    expected_output=True,
    label="le_test"
)
engine.register(compare_le)

@brick("compare_gt", description="[MICRO] Greater than")
def compare_gt(a: Any, b: Any) -> bool:
    """Check greater than."""
    return a > b

compare_gt.add_test(
    inputs={"a": 10, "b": 5},
    expected_output=True,
    label="gt_test"
)
engine.register(compare_gt)

@brick("compare_ge", description="[MICRO] Greater or equal")
def compare_ge(a: Any, b: Any) -> bool:
    """Check greater or equal."""
    return a >= b

compare_ge.add_test(
    inputs={"a": 10, "b": 10},
    expected_output=True,
    label="ge_test"
)
engine.register(compare_ge)

@brick("compare_zero", description="[MICRO] Is zero")
def compare_zero(a: int) -> bool:
    """Check if zero."""
    return a == 0

compare_zero.add_test(
    inputs={"a": 0},
    expected_output=True,
    label="zero_test"
)
engine.register(compare_zero)

@brick("compare_sign", description="[MICRO] Get sign")
def compare_sign(a: int) -> int:
    """Get sign: -1, 0, or 1."""
    if a < 0: return -1
    if a > 0: return 1
    return 0

compare_sign.add_test(
    inputs={"a": -42},
    expected_output=-1,
    label="sign_test"
)
engine.register(compare_sign)

@brick("compare_range", description="[MICRO] In range check")
def compare_range(value: int, min_val: int, max_val: int) -> bool:
    """Check if value in range [min, max]."""
    return min_val <= value <= max_val

compare_range.add_test(
    inputs={"value": 5, "min_val": 1, "max_val": 10},
    expected_output=True,
    label="range_test"
)
engine.register(compare_range)

@brick("compare_null", description="[MICRO] Is null/None")
def compare_null(a: Any) -> bool:
    """Check if None."""
    return a is None

compare_null.add_test(
    inputs={"a": None},
    expected_output=True,
    label="null_test"
)
engine.register(compare_null)

print(f"  ✅ Comparison: 10/10 micro-bricks")

# ===== CONTROL FLOW (10) =====
print("\n[5/5] Building Control Flow Operations (10)...")

@brick("return_value", description="[MICRO] Return value")
def return_value(value: Any) -> Any:
    """Return a value (identity function)."""
    return value

return_value.add_test(
    inputs={"value": 42},
    expected_output=42,
    label="return_test"
)
engine.register(return_value)

@brick("call_function", description="[MICRO] Call function")
def call_function(func: Callable, arg: Any) -> Any:
    """Call a function with one argument."""
    return func(arg)

call_function.add_test(
    inputs={"func": lambda x: x * 2, "arg": 21},
    expected_output=42,
    label="call_test"
)
engine.register(call_function)

@brick("branch_if", description="[MICRO] Conditional branch")
def branch_if(condition: bool, true_val: Any, false_val: Any) -> Any:
    """Branch based on condition."""
    return true_val if condition else false_val

branch_if.add_test(
    inputs={"condition": True, "true_val": "yes", "false_val": "no"},
    expected_output="yes",
    label="branch_test"
)
engine.register(branch_if)

@brick("loop_counter", description="[MICRO] Loop counter")
def loop_counter(current: int, step: int, limit: int) -> dict:
    """Update loop counter, check if done."""
    next_val = current + step
    done = (step > 0 and next_val >= limit) or (step < 0 and next_val <= limit)
    return {"value": next_val, "done": done}

loop_counter.add_test(
    inputs={"current": 0, "step": 1, "limit": 10},
    expected_output={"value": 1, "done": False},
    label="counter_test"
)
engine.register(loop_counter)

@brick("select_value", description="[MICRO] Select from options")
def select_value(index: int, options: list) -> Any:
    """Select value by index."""
    return options[index] if 0 <= index < len(options) else None

select_value.add_test(
    inputs={"index": 1, "options": ["a", "b", "c"]},
    expected_output="b",
    label="select_test"
)
engine.register(select_value)

@brick("error_raise", description="[MICRO] Raise error")
def error_raise(message: str, error_type: str = "RuntimeError") -> dict:
    """Signal an error (returns error info)."""
    return {"error": True, "type": error_type, "message": message}

error_raise.add_test(
    inputs={"message": "Test error"},
    expected_output={"error": True, "type": "RuntimeError", "message": "Test error"},
    label="error_test"
)
engine.register(error_raise)

@brick("error_catch", description="[MICRO] Catch error")
def error_catch(result: dict, default: Any = None) -> Any:
    """Catch error and return default."""
    if isinstance(result, dict) and result.get("error"):
        return default
    return result

error_catch.add_test(
    inputs={"result": {"error": True}, "default": 0},
    expected_output=0,
    label="catch_test"
)
engine.register(error_catch)

@brick("noop", description="[MICRO] No operation")
def noop() -> None:
    """No operation (NOP)."""
    pass

noop.add_test(
    inputs={},
    expected_output=None,
    label="noop_test"
)
engine.register(noop)

@brick("identity", description="[MICRO] Identity function")
def identity(value: Any) -> Any:
    """Return input unchanged."""
    return value

identity.add_test(
    inputs={"value": "test"},
    expected_output="test",
    label="identity_test"
)
engine.register(identity)

@brick("const_value", description="[MICRO] Return constant")
def const_value(value: Any) -> Callable:
    """Return a function that always returns value."""
    return lambda: value

const_value.add_test(
    inputs={"value": 42},
    expected_output=lambda x: callable(x) and x() == 42,
    label="const_test"
)
engine.register(const_value)

print(f"  ✅ Control Flow: 10/10 micro-bricks")

# ===== SUMMARY =====
print("\n" + "=" * 80)
print("EPIC 2 - Phase 1 COMPLETE!")
print("=" * 80)
print(f"\n✅ Total micro-bricks: {len(engine.bricks)}")
print(f"✅ Memory: 10 micro-bricks")
print(f"✅ Arithmetic: 10 micro-bricks")
print(f"✅ Logic: 10 micro-bricks")
print(f"✅ Comparison: 10 micro-bricks")
print(f"✅ Control Flow: 10 micro-bricks")
print(f"\nAll 50 assembly-level primitives ready!")
print("\nNext: Build the TRANSLATOR! (Phase 2)")
print("=" * 80)
