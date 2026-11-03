import pytest
from photo_print_order import extra_print_charge, order_valid, dispatch_status


# ---------- extra_print_charge ----------
def test_within_included_prints():
    assert extra_print_charge("4x6", 15, "matte", False) == 0


def test_unknown_print_size_raises():
    with pytest.raises(ValueError):
        extra_print_charge("12x18", 10, "matte", False)


def test_negative_copies_raises():
    with pytest.raises(ValueError):
        extra_print_charge("4x6", -1, "matte", False)


def test_member_bonus_applied():
    # 4x6 member: 20 + 5 = 25 included, so 25 copies are free
    assert extra_print_charge("4x6", 25, "matte", True) == 0


def test_matte_extra_charge():
    # 4x6 non-member: 20 included, 10 extra at Rs.4
    assert extra_print_charge("4x6", 30, "matte", False) == 40


def test_glossy_extra_charge():
    # 10 extra at Rs.7
    assert extra_print_charge("4x6", 30, "glossy", False) == 70


def test_bulk_surcharge_canvas():
    # 80 extra, rate 7 + 2 (bulk) + 5 (canvas) = 14
    assert extra_print_charge("4x6", 100, "canvas", False) == 1120


# ---------- order_valid ----------
def test_order_valid():
    assert order_valid(10, 100, False) is True


def test_rush_order():
    assert order_valid(10, 40, True) is True


def test_file_too_large():
    assert order_valid(30, 10, False) is False


# ---------- dispatch_status ----------
def test_dispatch_on_time_unframed():
    assert dispatch_status(12, False, False) == "on_time"


def test_dispatch_tight_framed():
    assert dispatch_status(20, True, False) == "tight"


def test_dispatch_missed_international():
    assert dispatch_status(5, False, True) == "missed"
