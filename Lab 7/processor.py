"""Photo print order processing (hardened against invalid input)."""
import math

INCLUDED_PRINTS = {"4x6": 20, "5x7": 15, "8x10": 10}
FINISHES = ("matte", "glossy", "canvas")


def _require_int(value, name):
    """Return value if it is a real int (bool is rejected), else ValueError."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"invalid {name}")
    return value


def _require_bool(value, name):
    """Return value if it is a real bool, else ValueError."""
    if not isinstance(value, bool):
        raise ValueError(f"invalid {name}")
    return value


def _require_non_negative_number(value, name):
    """Return value if it is a finite, non-negative int/float, else ValueError."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"invalid {name}")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"invalid {name}")
    if value < 0:
        raise ValueError(f"invalid {name}")
    return value


def extra_print_charge(print_size, copies, finish, is_member):
    """Return the extra charge (Rs.) for copies beyond the included prints."""
    if not isinstance(print_size, str) or print_size not in INCLUDED_PRINTS:
        raise ValueError("unknown print size")
    _require_int(copies, "copies")
    if copies < 0:
        raise ValueError("invalid copies")
    if not isinstance(finish, str) or finish not in FINISHES:
        raise ValueError("unknown finish")
    _require_bool(is_member, "is_member")

    included = INCLUDED_PRINTS[print_size]
    if is_member and print_size != "8x10":
        included += 5
    extra = copies - included
    if extra <= 0:
        return 0
    if finish == "matte":
        rate = 4
    else:
        rate = 7
    if extra > 50:
        rate = rate + 2
        if finish == "canvas":
            rate += 5
    return extra * rate


def order_valid(file_mb, copies, is_rush):
    """Return True if the order is within file-size and copy limits."""
    _require_non_negative_number(file_mb, "file size")
    _require_int(copies, "copies")
    if copies < 0:
        raise ValueError("invalid copies")
    _require_bool(is_rush, "is_rush")

    if is_rush:
        return copies <= 50
    if file_mb > 25:
        return False
    return copies <= 500


def dispatch_status(hours_before_dispatch, is_framed, is_international):
    """Return 'on_time', 'tight' or 'missed' for the hours left to dispatch."""
    _require_non_negative_number(hours_before_dispatch, "hours")
    _require_bool(is_framed, "is_framed")
    _require_bool(is_international, "is_international")

    if is_framed:
        cutoff = 24
    else:
        cutoff = 12
    if is_international:
        cutoff += 24
    if hours_before_dispatch >= cutoff:
        return "on_time"
    elif hours_before_dispatch >= cutoff - 6:
        return "tight"
    return "missed"


if __name__ == "__main__":
    print("Extra charge (4x6, 30 copies, matte, non-member):",
          extra_print_charge("4x6", 30, "matte", False))
    print("Extra charge (4x6, 100 copies, canvas, non-member):",
          extra_print_charge("4x6", 100, "canvas", False))
    print("Order valid (10 MB, 100 copies, no rush):",
          order_valid(10, 100, False))
    print("Order valid (10 MB, 51 copies, rush):",
          order_valid(10, 51, True))
    print("Dispatch status (12h, unframed, domestic):",
          dispatch_status(12, False, False))
    print("Dispatch status (5h, unframed, domestic):",
          dispatch_status(5, False, False))
    for label, call in [
        ("None copies", lambda: extra_print_charge("4x6", None, "matte", False)),
        ("NaN file size", lambda: order_valid(float("nan"), 10, False)),
        ("string hours", lambda: dispatch_status("soon", False, False)),
    ]:
        try:
            call()
        except ValueError as e:
            print(f"Rejected bad input ({label}): {e}")
