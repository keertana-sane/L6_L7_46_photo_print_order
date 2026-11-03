import pytest
from photo_print_order import extra_print_charge, order_valid, dispatch_status


# ---------- extra_print_charge ----------
def test_within_included_prints():
    assert extra_print_charge("4x6", 15, "matte", False) == 0


def test_unknown_print_size_raises():
    with pytest.raises(ValueError, match="unknown print size"):
        extra_print_charge("12x18", 10, "matte", False)


def test_negative_copies_raises():
    with pytest.raises(ValueError, match="invalid copies"):
        extra_print_charge("4x6", -1, "matte", False)


def test_zero_copies_is_free():
    # copies == 0 is valid (not < 0) and costs nothing
    assert extra_print_charge("4x6", 0, "matte", False) == 0


def test_member_bonus_applied():
    # 4x6 member: 20 + 5 = 25 included
    assert extra_print_charge("4x6", 25, "matte", True) == 0
    assert extra_print_charge("4x6", 26, "matte", True) == 4


def test_member_no_bonus_for_8x10():
    # 8x10 member gets no bonus: 10 included, 1 extra at Rs.4
    assert extra_print_charge("8x10", 11, "matte", True) == 4


def test_non_member_no_bonus():
    assert extra_print_charge("4x6", 21, "matte", False) == 4


def test_exactly_at_included_boundary():
    # extra == 0 -> free
    assert extra_print_charge("5x7", 15, "glossy", False) == 0


def test_matte_extra_charge():
    assert extra_print_charge("4x6", 30, "matte", False) == 40


def test_glossy_extra_charge():
    assert extra_print_charge("4x6", 30, "glossy", False) == 70


def test_bulk_boundary_exactly_50_extra_no_surcharge():
    # extra == 50 -> NOT > 50, so base rate only
    assert extra_print_charge("4x6", 70, "matte", False) == 200


def test_bulk_just_over_50_matte():
    # extra == 51 -> rate 4 + 2 = 6, not canvas
    assert extra_print_charge("4x6", 71, "matte", False) == 51 * 6


def test_bulk_canvas_surcharge():
    # extra 80, rate 7 + 2 + 5 = 14
    assert extra_print_charge("4x6", 100, "canvas", False) == 1120


def test_canvas_without_bulk_has_no_surcharge():
    # canvas only adds +5 when extra > 50
    assert extra_print_charge("4x6", 30, "canvas", False) == 70


# ---------- order_valid ----------
def test_order_valid():
    assert order_valid(10, 100, False) is True


def test_rush_within_limit():
    assert order_valid(10, 50, True) is True


def test_rush_over_limit():
    assert order_valid(10, 51, True) is False


def test_rush_ignores_file_size():
    assert order_valid(100, 10, True) is True


def test_file_too_large():
    assert order_valid(26, 10, False) is False


def test_file_exactly_25_mb_ok():
    assert order_valid(25, 10, False) is True


def test_normal_copies_limit():
    assert order_valid(10, 500, False) is True
    assert order_valid(10, 501, False) is False


# ---------- dispatch_status ----------
def test_dispatch_on_time_unframed():
    assert dispatch_status(12, False, False) == "on_time"


def test_dispatch_tight_unframed():
    assert dispatch_status(6, False, False) == "tight"


def test_dispatch_missed_unframed():
    assert dispatch_status(5, False, False) == "missed"


def test_dispatch_framed_cutoff_24():
    assert dispatch_status(24, True, False) == "on_time"
    assert dispatch_status(18, True, False) == "tight"
    assert dispatch_status(17, True, False) == "missed"


def test_dispatch_international_adds_24():
    assert dispatch_status(36, False, True) == "on_time"
    assert dispatch_status(30, False, True) == "tight"
    assert dispatch_status(29, False, True) == "missed"


def test_dispatch_framed_international():
    # cutoff = 24 + 24 = 48
    assert dispatch_status(48, True, True) == "on_time"
    assert dispatch_status(42, True, True) == "tight"
    assert dispatch_status(41, True, True) == "missed"
