from typing import List
from .schema import Invoice

class CompletenessRule:
    def check(self, inv: Invoice) -> List[str]:
        errors = []
        if not inv.invoice_number: errors.append('MISSING_INVOICE_NUMBER')
        if not inv.invoice_date: errors.append('MISSING_INVOICE_DATE')
        if not inv.seller_name: errors.append('MISSING_SELLER_NAME')
        if not inv.buyer_name: errors.append('MISSING_BUYER_NAME')
        if inv.net_total < 0 or inv.tax_amount < 0 or inv.gross_total < 0: errors.append('NEGATIVE_TOTALS')
        return errors

class DateLogicRule:
    def check(self, inv: Invoice) -> List[str]:
        errors = []
        if inv.due_date and inv.due_date < inv.invoice_date: errors.append('DUE_DATE_BEFORE_INVOICE')
        return errors

class TotalsMathRule:
    def check(self, inv: Invoice) -> List[str]:
        errors = []
        if abs(inv.gross_total - (inv.net_total + inv.tax_amount)) > 0.01: errors.append('TOTALS_MISMATCH')
        if inv.line_items:
            sum_lines = sum(item.line_total for item in inv.line_items)
            if abs(sum_lines - inv.net_total) > 0.01: errors.append('LINES_SUM_MISMATCH')
        return errors

class DuplicateRule:
    def __init__(self, seen: set):
        self.seen = seen

    def check(self, inv: Invoice) -> List[str]:
        key = (inv.invoice_number, inv.seller_name, inv.invoice_date)
        if key in self.seen: return ['DUPLICATE_INVOICE']
        self.seen.add(key)
        return []