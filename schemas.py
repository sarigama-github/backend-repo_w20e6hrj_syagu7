"""
Database Schemas for the Artist Commission Organizer

Each Pydantic model represents a collection in MongoDB (collection name = lowercase class name).
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class Client(BaseModel):
    display_name: str = Field(..., description="Client preferred name")
    email: Optional[str] = Field(None, description="Contact email")
    socials: Optional[str] = Field(None, description="Social handle or link")
    notes: Optional[str] = Field(None, description="Private notes about the client")

class Commission(BaseModel):
    title: str = Field(..., description="Commission title")
    client_id: Optional[str] = Field(None, description="Related client id as string")
    status: str = Field("New", description="Pipeline status: New, Sketch, In Progress, Review, Delivered, On Hold")
    due_date: Optional[datetime] = Field(None, description="Deadline for delivery")
    price: Optional[float] = Field(None, ge=0, description="Agreed price")
    currency: str = Field("EUR", description="Currency code")
    tags: List[str] = Field(default_factory=list, description="Labels for quick filtering")
    brief: Optional[str] = Field(None, description="Short description or requirements")

class Note(BaseModel):
    commission_id: str = Field(..., description="Linked commission id")
    content: str = Field(..., description="Note body")
    mood: Optional[str] = Field(None, description="Optional mood tag")
