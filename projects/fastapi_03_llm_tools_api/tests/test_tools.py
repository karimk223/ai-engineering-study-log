import pytest
from pydantic import ValidationError

from app.tools import get_order_status


@pytest.mark.parametrize(
    "order_id, expected_status",
    [
        (101, "processing"),
        (102, "shipped"),
        (103, "delivered"),
    ],
)
def test_known_order(order_id, expected_status):
    result = get_order_status(order_id)

    assert result == {
        "order_id": order_id,
        "found": True,
        "status": expected_status,
    }


def test_unknown_order():
    assert get_order_status(999) == {
        "order_id": 999,
        "found": False,
        "status": None,
    }


@pytest.mark.parametrize(
    "invalid_id",
    [
        0,
        -1,
        "102",
        102.0,
        True,
        None,
        9_223_372_036_854_775_808,
        [],
        {},
    ],
)
def test_invalid_order_id(invalid_id):
    with pytest.raises(ValidationError):
        get_order_status(invalid_id)