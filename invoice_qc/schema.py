# invoice_qc/schema.py
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, field_validator, model_validator


class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    line_total: float

    @model_validator(mode='after')
    def check_math(self):
        if abs(self.quantity * self.unit_price - self.line_total) > 0.01:
            raise ValueError(f"Line math wrong: {self.quantity} × {self.unit_price} ≠ {self.line_total}")
        return self


class Invoice(BaseModel):
    invoice_number: str
    invoice_date: date
    due_date: Optional[date] = None

    seller_name: str
    seller_address: Optional[str] = None
    seller_tax_id: Optional[str] = None

    buyer_name: str
    buyer_address: Optional[str] = None
    buyer_tax_id: Optional[str] = None

    currency: str = "EUR"
    net_total: float
    tax_amount: float
    gross_total: float

    payment_terms: Optional[str] = None
    iban: Optional[str] = None

    line_items: List[LineItem] = []
    source_file: Optional[str] = None

    # Core validations
    @field_validator("invoice_number", "seller_name", "buyer_name")
    @classmethod
    def not_empty(cls, v):
        if not v or not str(v).strip():
            raise ValueError("Required field missing or empty")
        return str(v).strip()

    @field_validator("net_total", "tax_amount", "gross_total")
    @classmethod
    def non_negative(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v

    @model_validator(mode='after')
    def totals_match(self):
        if abs(self.gross_total - (self.net_total + self.tax_amount)) > 0.01:
            raise ValueError("gross ≠ net + tax")
        return self

    @model_validator(mode='after')
    def line_items_match_net(self):
        if self.line_items:
            calc = sum(item.line_total for item in self.line_items)
            if abs(calc - self.net_total) > 0.01:
                raise ValueError(f"Line items sum ({calc}) ≠ net_total ({self.net_total})")
        return self