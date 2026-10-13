from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field, StrictStr
from app.database import (
    init_database,
    save_request,
    get_request,
    update_request,
    delete_request,
    list_requests,
)
from contextlib import asynccontextmanager
from typing import Annotated

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(title="Customer Requests API", lifespan=lifespan)

SQLITE_MAX_INTEGER = 9_223_372_036_854_775_807

RequestId = Annotated[
    int,
    Path(ge=1, le=SQLITE_MAX_INTEGER),
]

@app.get("/health")
def health():
        return {"status": "ok", "service": "customer-requests"}

class CustomerRequest(BaseModel):
    customer_name: StrictStr = Field(min_length=1, max_length=100)
    message: StrictStr = Field(min_length=1, max_length=2000)

    class Config:
        anystr_strip_whitespace = True
        extra = "forbid"


@app.post("/requests", status_code=201)
def receive_request(customer_request: CustomerRequest):
    request_id = save_request(
        customer_request.customer_name,
        customer_request.message,
    )
    return {
        "id": request_id,
        "status": "received",
        "customer_name": customer_request.customer_name,
        "message": customer_request.message,
    }

@app.get("/requests/{request_id}")
def read_request(request_id: RequestId):
    request_record = get_request(request_id)
    if request_record is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return request_record

@app.put("/requests/{request_id}")
def edit_request(request_id: RequestId, customer_request: CustomerRequest):
    request_record = update_request(
        request_id,
        customer_request.customer_name,
        customer_request.message,
    )
    if request_record is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return request_record

@app.delete("/requests/{request_id}")
def remove_request(request_id: RequestId):
    was_deleted = delete_request(request_id)
    if not was_deleted:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"status": "deleted", "id": request_id}

@app.get("/requests")
def read_requests(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=1_000_000),
):
    return {
        "items": list_requests(limit, offset),
        "limit": limit,
        "offset": offset,
    }
