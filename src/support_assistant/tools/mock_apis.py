from __future__ import annotations

from typing import Any

# fake db, no real database needed
_ORDERS: dict[str, dict[str, Any]] = {
    "12345": {"status": "in_transit", "carrier": "DHL", "eta_days": 2},
    "98765": {"status": "delivered", "carrier": "FedEx", "delivered_on": "2026-05-20"},
    "55555": {"status": "processing", "carrier": None, "eta_days": 5},
}

_PRODUCTS: dict[str, dict[str, Any]] = {
    "thunder x1 headphones": {
        "category": "audio",
        "battery_life_hours": 30,
        "connectivity": "Bluetooth 5.3",
        "warranty_months": 24,
        "note": "Active noise cancellation, USB-C fast charging.",
    },
    "aurora smartwatch": {
        "category": "wearable",
        "battery_life_hours": 168,
        "connectivity": "Bluetooth 5.0, Wi-Fi",
        "warranty_months": 12,
        "note": "Water resistant to 50m, built-in GPS.",
    },
}

_DEFAULT_STATUS = {"status": "unknown", "note": "No matching order found."}
_DEFAULT_PRODUCT = {"category": "unknown", "note": "No spec sheet for this product."}


# sales: get order status by id
def get_order_status(order_id: str) -> dict[str, Any]:
    order_id = str(order_id).strip().lstrip("#")
    record = _ORDERS.get(order_id, _DEFAULT_STATUS)
    return {"order_id": order_id, **record}


# technical: product info by name
def get_product_info(product_name: str) -> dict[str, Any]:
    key = str(product_name).strip().lower()
    record = _PRODUCTS.get(key)
    if record is None:
        # try partial match
        for name, rec in _PRODUCTS.items():
            if name in key or key in name:
                record = rec
                break
    return {"product_name": product_name, **(record or _DEFAULT_PRODUCT)}


# financial: refund rules. no args
def get_refund_policy() -> dict[str, Any]:
    return {
        "policy": (
            "You may request a full refund within 30 days of delivery, "
            "provided the item is unused and in its original packaging. "
            "Refunds are processed to the original payment method within "
            "5 to 7 business days after we receive the returned item. "
            "Shipping costs are non-refundable unless the return is due to "
            "our error."
        ),
        "window_days": 30,
        "processing_days": "5-7 business days",
    }
