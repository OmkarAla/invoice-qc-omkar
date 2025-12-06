# invoice_qc/validator.py
from typing import List
from datetime import date
from pydantic import ValidationError
from .schema import Invoice


class ValidationResult:
    def __init__(self, invoice: Invoice, errors: List[str]):
        self.invoice = invoice
        self.errors = errors
        self.is_valid = len(errors) == 0

    def to_dict(self):
        return {
            "invoice_number": self.invoice.invoice_number,
            "source_file": self.invoice.source_file,
            "is_valid": self.is_valid,
            "errors": self.errors
        }


def validate_invoices(invoices: List[Invoice]) -> List[ValidationResult]:
    results = []
    seen = set()

    for inv in invoices:
        errors = []

        # Pydantic validation
        try:
            inv.model_validate(inv.model_dump())
        except ValidationError as e:
            for err in e.errors():
                field = " → ".join(str(x) for x in err["loc"])
                errors.append(f"{field}: {err['msg']}")

        # Business rules
        if inv.invoice_date > date.today():
            errors.append("Invoice date in the future")

        if inv.due_date and inv.due_date < inv.invoice_date:
            errors.append("Due date before invoice date")

        # Duplicate check
        key = (inv.invoice_number, inv.seller_name, inv.invoice_date)
        if key in seen:
            errors.append("Possible duplicate")
        seen.add(key)

        results.append(ValidationResult(inv, errors))

    return results


def print_validation_report(results: List[ValidationResult]):
    valid = sum(1 for r in results if r.is_valid)
    print(f"\nValidation Complete")
    print(f"Valid: {valid}/{len(results)}")
    if valid < len(results):
        print("\nIssues:")
        for r in results:
            if not r.is_valid:
                print(f"  • {r.invoice.invoice_number} ({r.invoice.source_file})")
                for e in r.errors:
                    print(f"    → {e}")