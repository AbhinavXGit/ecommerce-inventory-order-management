from typing import List

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    category: str = Field(min_length=2, max_length=50)
    price: float = Field(gt=0)


class InventoryUpdate(BaseModel):
    stock: int = Field(ge=0)


class InventoryAdd(BaseModel):
    quantity: int = Field(gt=0)


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=150)


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)
    items: List[OrderItemCreate] = Field(min_length=1)
