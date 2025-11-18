"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# Example schemas (kept for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Seating application schemas

class SeatInline(BaseModel):
    index: int = Field(..., ge=0, description="Seat index at the table")
    label: str = Field(..., description="Human-friendly seat label")
    reserved: bool = Field(False, description="Reservation status")

class Table(BaseModel):
    name: str = Field(..., description="Table name/label")
    shape: Literal["round", "rect"] = Field("round", description="Table shape")
    x: float = Field(..., ge=0, description="Position X in room units")
    y: float = Field(..., ge=0, description="Position Y in room units")
    width: float = Field(120, gt=0, description="Width in room units")
    height: float = Field(120, gt=0, description="Height in room units")
    rotation: float = Field(0, description="Rotation angle in degrees")
    color: Optional[str] = Field(None, description="Optional accent color for the table")
    seats: List[SeatInline] = Field(default_factory=list, description="Seats at the table")

class Reservation(BaseModel):
    table_id: str = Field(..., description="Table document id")
    seat_index: int = Field(..., ge=0, description="Seat index being reserved")
    name: str = Field(..., description="Guest name")
    note: Optional[str] = Field(None, description="Optional note or occasion")
