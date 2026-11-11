"""Hypothesis fuzz tests for processor.py (photo print order).

Properties checked for all three functions:
  1. They never crash with anything other than a deliberate ValueError,
     no matter what garbage is passed in (None, str, list, NaN, inf, ...).
  2. For valid inputs the results are sane (right type, right range,
     monotonic behaviour, boundaries).
"""
import math

import pytest
from hypothesis import given, settings, strategies as st

from processor import extra_print_charge, order_valid, dispatch_status

SIZES = ["4x6", "5x7", "8x10"]
FINISHES = ["matte", "glossy", "canvas"]

# Anything at all: the "unexpected input" generator.
anything = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=True, allow_infinity=True),
    st.text(),
    st.binary(),
    st.lists(st.integers()),
    st.dictionaries(st.text(), st.integers()),
)

valid_copies = st.integers(min_value=0, max_value=10_000)
valid_hours = st.floats(min_value=0, max_value=1_000,
                        allow_nan=False, allow_infinity=False)


def only_value_error(func, *args):
    """Call func; a ValueError is acceptable, any other exception is a bug."""
    try:
        return func(*args)
    except ValueError:
        return None
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"{func.__name__}{args!r} crashed with "
                    f"{type(e).__name__}: {e}")


# ---------------------------------------------------------------- extra_print_charge
@settings(max_examples=300, deadline=None)
@given(anything, anything, anything, anything)
def test_extra_print_charge_never_crashes(size, copies, finish, member):
    result = only_value_error(extra_print_charge, size, copies, finish, member)
    if result is not None:
        assert isinstance(result, (int, float))
        assert result >= 0


@given(st.sampled_from(SIZES), valid_copies, st.sampled_from(FINISHES),
       st.booleans())
def test_extra_print_charge_valid_is_non_negative_number(size, copies, finish,
                                                         member):
    result = extra_print_charge(size, copies, finish, member)
    assert isinstance(result, (int, float))
    assert not math.isnan(result)
    assert result >= 0


@given(st.sampled_from(SIZES), st.sampled_from(FINISHES), st.booleans(),
       st.integers(min_value=0, max_value=5_000))
def test_extra_print_charge_more_copies_never_cheaper(size, finish, member, n):
    # a bulk surcharge makes it jump up, but it must never go down
    assert (extra_print_charge(size, n + 1, finish, member)
            >= extra_print_charge(size, n, finish, member))


@given(st.sampled_from(SIZES), st.sampled_from(FINISHES), st.booleans())
def test_extra_print_charge_member_never_pays_more(size, finish, member):
    for copies in (0, 5, 20, 25, 26, 75, 200):
        assert (extra_print_charge(size, copies, finish, True)
                <= extra_print_charge(size, copies, finish, False))


@given(anything.filter(lambda s: not isinstance(s, str) or s not in SIZES),
       valid_copies, st.sampled_from(FINISHES), st.booleans())
def test_extra_print_charge_bad_size_rejected(size, copies, finish, member):
    with pytest.raises(ValueError):
        extra_print_charge(size, copies, finish, member)


@given(st.sampled_from(SIZES),
       st.integers(max_value=-1), st.sampled_from(FINISHES), st.booleans())
def test_extra_print_charge_negative_copies_rejected(size, copies, finish,
                                                     member):
    with pytest.raises(ValueError):
        extra_print_charge(size, copies, finish, member)


@given(st.sampled_from(SIZES),
       anything.filter(lambda c: not (isinstance(c, int)
                                      and not isinstance(c, bool))),
       st.sampled_from(FINISHES), st.booleans())
def test_extra_print_charge_non_integer_copies_rejected(size, copies, finish,
                                                        member):
    with pytest.raises(ValueError):
        extra_print_charge(size, copies, finish, member)


@given(st.sampled_from(SIZES), valid_copies,
       st.text().filter(lambda f: f not in FINISHES), st.booleans())
def test_extra_print_charge_unknown_finish_rejected(size, copies, finish,
                                                    member):
    with pytest.raises(ValueError):
        extra_print_charge(size, copies, finish, member)


# ---------------------------------------------------------------- order_valid
@settings(max_examples=300, deadline=None)
@given(anything, anything, anything)
def test_order_valid_never_crashes(file_mb, copies, is_rush):
    result = only_value_error(order_valid, file_mb, copies, is_rush)
    if result is not None:
        assert isinstance(result, bool)


@given(st.floats(min_value=0, max_value=1_000, allow_nan=False,
                 allow_infinity=False),
       valid_copies, st.booleans())
def test_order_valid_returns_bool_for_valid_input(file_mb, copies, is_rush):
    assert isinstance(order_valid(file_mb, copies, is_rush), bool)


@given(st.integers(min_value=0, max_value=50),
       st.floats(min_value=0, max_value=25, allow_nan=False,
                 allow_infinity=False),
       st.booleans())
def test_order_valid_small_orders_are_valid(copies, file_mb, is_rush):
    assert order_valid(file_mb, copies, is_rush) is True


@given(st.floats(min_value=25.0001, max_value=1_000, allow_nan=False,
                 allow_infinity=False),
       valid_copies)
def test_order_valid_oversize_file_rejected_unless_rush(file_mb, copies):
    assert order_valid(file_mb, copies, False) is False


@given(st.one_of(st.just(float("nan")),
                 st.just(float("inf")),
                 st.just(float("-inf")),
                 st.floats(max_value=-0.0001, allow_nan=False,
                           allow_infinity=False)))
def test_order_valid_bad_file_size_rejected(file_mb):
    with pytest.raises(ValueError):
        order_valid(file_mb, 10, False)


@given(st.integers(max_value=-1), st.booleans())
def test_order_valid_negative_copies_rejected(copies, is_rush):
    with pytest.raises(ValueError):
        order_valid(10, copies, is_rush)


@given(anything.filter(lambda b: not isinstance(b, bool)))
def test_order_valid_non_bool_rush_rejected(is_rush):
    with pytest.raises(ValueError):
        order_valid(10, 10, is_rush)


# ---------------------------------------------------------------- dispatch_status
@settings(max_examples=300, deadline=None)
@given(anything, anything, anything)
def test_dispatch_status_never_crashes(hours, framed, international):
    result = only_value_error(dispatch_status, hours, framed, international)
    if result is not None:
        assert result in ("on_time", "tight", "missed")


@given(valid_hours, st.booleans(), st.booleans())
def test_dispatch_status_valid_returns_known_status(hours, framed,
                                                    international):
    assert dispatch_status(hours, framed, international) in (
        "on_time", "tight", "missed")


@given(valid_hours, st.floats(min_value=0, max_value=500, allow_nan=False,
                              allow_infinity=False),
       st.booleans(), st.booleans())
def test_dispatch_status_more_time_never_worse(hours, extra, framed,
                                               international):
    rank = {"missed": 0, "tight": 1, "on_time": 2}
    assert (rank[dispatch_status(hours + extra, framed, international)]
            >= rank[dispatch_status(hours, framed, international)])


@given(st.booleans(), st.booleans())
def test_dispatch_status_cutoff_boundaries(framed, international):
    cutoff = (24 if framed else 12) + (24 if international else 0)
    assert dispatch_status(cutoff, framed, international) == "on_time"
    assert dispatch_status(cutoff - 6, framed, international) == "tight"
    assert dispatch_status(cutoff - 6.01, framed, international) == "missed"


@given(st.one_of(st.just(float("nan")), st.just(float("inf")),
                 st.just(float("-inf")),
                 st.floats(max_value=-0.0001, allow_nan=False,
                           allow_infinity=False)),
       st.booleans(), st.booleans())
def test_dispatch_status_bad_hours_rejected(hours, framed, international):
    with pytest.raises(ValueError):
        dispatch_status(hours, framed, international)


@given(anything.filter(lambda h: isinstance(h, (str, bytes, list, dict))
                       or h is None or isinstance(h, bool)),
       st.booleans(), st.booleans())
def test_dispatch_status_non_numeric_hours_rejected(hours, framed,
                                                    international):
    with pytest.raises(ValueError):
        dispatch_status(hours, framed, international)


@given(valid_hours,
       anything.filter(lambda b: not isinstance(b, bool)), st.booleans())
def test_dispatch_status_non_bool_flags_rejected(hours, flag, other):
    with pytest.raises(ValueError):
        dispatch_status(hours, flag, other)
    with pytest.raises(ValueError):
        dispatch_status(hours, other, flag)
