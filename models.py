from pydantic import BaseModel, Field, EmailStr, field_validator
import phonenumbers
from typing import List, Optional
import re

class TechStack(BaseModel):
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)

class CandidateInfo(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    years_experience: int = Field(ge=0, le=50)
    desired_position: str
    current_location: str
    tech_stack: TechStack

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Phone number must be in a valid format")

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if len(v.strip().split()) < 2:
            raise ValueError("Please provide both first and last name")
        if not re.match(r"^[a-zA-Z\s\-'.]+$", v):
            raise ValueError("Name can only contain letters, spaces, hyphens, apostrophes, and periods")
        return v.title()

    @field_validator('current_location')
    @classmethod
    def validate_location(cls, v):
        if not re.match(r"^[a-zA-Z\s\,]+$", v) or v.count(',') != 1:
            raise ValueError("Location must be in 'City, Country' format")
        return v