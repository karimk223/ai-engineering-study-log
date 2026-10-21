from pydantic import BaseModel, ConfigDict, Field


class OrderStatusArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_id: int = Field(strict=True, ge=1, le=9_223_372_036_854_775_807)


ORDER_STATUSES = {
    101: "processing",
    102: "shipped",
    103: "delivered",
}


def get_order_status(order_id: int) -> dict:
    args = OrderStatusArgs(order_id=order_id)
    status = ORDER_STATUSES.get(args.order_id)

    return {
        "order_id": args.order_id,
        "found": status is not None,
        "status": status,
    }

ORDER_STATUS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_order_status",
        "description": "Read the status of one fictional order using its order ID.",
        "parameters": OrderStatusArgs.model_json_schema(),
    },
}