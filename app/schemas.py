from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field
)


# =========================================================
# Registration
# =========================================================

class RegisterInput(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=40,
        pattern=r"^[A-Za-z0-9_.-]+$"
    )

    email: EmailStr

    full_name: Optional[str] = Field(
        default=None,
        max_length=100
    )

    password: str = Field(
        min_length=6,
        max_length=128
    )


# =========================================================
# Home Interior
# =========================================================

class HomeBudgetInput(BaseModel):

    total_budget: float = Field(
        gt=0
    )

    num_lights: int = Field(
        default=0,
        ge=0,
        le=100
    )

    num_fans: int = Field(
        default=0,
        ge=0,
        le=100
    )

    num_furniture: int = Field(
        default=0,
        ge=0,
        le=100
    )

    num_dining_tables: int = Field(
        default=0,
        ge=0,
        le=20
    )

    has_living_room: bool = False

    has_kitchen: bool = False

    has_bedroom: bool = False

    additional_requirements: Optional[str] = Field(
        default="",
        max_length=1000
    )


# =========================================================
# Party
# =========================================================

class PartyBudgetInput(BaseModel):

    total_budget: float = Field(
        gt=0
    )

    party_type: str = Field(
        min_length=2,
        max_length=100
    )

    num_guests: int = Field(
        gt=0,
        le=10000
    )

    venue_type: Optional[str] = Field(
        default="",
        max_length=100
    )

    needs_catering: bool = True

    needs_decoration: bool = True

    needs_entertainment: bool = False

    additional_requirements: Optional[str] = Field(
        default="",
        max_length=1000
    )


# =========================================================
# Jewelry
# =========================================================

class JewelryBudgetInput(BaseModel):

    total_budget: float = Field(
        gt=0
    )

    occasion: str = Field(
        min_length=2,
        max_length=100
    )

    preferences: Optional[str] = Field(
        default="",
        max_length=1000
    )
    