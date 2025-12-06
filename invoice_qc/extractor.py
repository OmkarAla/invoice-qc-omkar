# invoice_qc/extractor.py
import pdfplumber
import re
from pathlib import Path
from datetime import date
from typing import List
from invoice_qc.schema import Invoice, LineItem


def clean_number(text):
    if not text:
        return 0.0
    matches = re.findall(r'[\d.,]+', str(text))
    if not matches:
        return 0.0
    num = matches[-1]
    num = num.replace(".", "").replace(",", ".")
    try:
        return float(num)
    except:
        return 0.0


def extract_from_pdf(pdf_path: Path) -> Invoice:
    data = {"source_file": pdf_path.name, "line_items": []}

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text() or ""
        table = page.extract_table() or []

    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    # 1. Bestellnummer
    for line in lines:
        m = re.search(r"AUFNR\s*(\d+)", line, re.I)
        if m:
            data["invoice_number"] = f"AUFNR{m.group(1)}"
            break

    # 2. Date
    for line in lines:
        m = re.search(r"vom\s+(\d{2}\.\d{2}\.\d{4})", line)
        if m:
            d, mth, y = map(int, m.group(1).split('.'))
            data["invoice_date"] = date(y, mth, d)
            break

    # 3. BUYER NAME — first line after "Kundenanschrift"
    buyer_name = "Unknown Buyer"
    found_kundenanschrift = False
    for line in lines:
        if "Kundenanschrift" in line:
            found_kundenanschrift = True
            continue
        if found_kundenanschrift and line and not line.startswith(("Seite", "Bestellung")):
            buyer_name = line
            break
    data["buyer_name"] = buyer_name

    # 4. SELLER NAME — NEW, PERFECT METHOD
    seller_name = "Unknown Supplier"
    found_buyer = False
    for line in lines:
        if buyer_name in line:  # the line that contains the buyer name
            found_buyer = True
            continue
        if found_buyer and line:
            # This is the line AFTER the buyer line
            # Clean it and take it as seller name
            cleaned = re.sub(r"\s*\([^)]*\)|Deutschland.*$|GmbH.*$|AG.*$", "", line, flags=re.I).strip()
            if cleaned:
                seller_name = cleaned
                break

    data["seller_name"] = seller_name

    # 5. Currency
    data["currency"] = "EUR"

    # 6. Totals
    for line in lines:
        if "Gesamtwert" in line and "MwSt" not in line and "inkl." not in line:
            data["net_total"] = clean_number(line)
        if "MwSt. 19" in line:
            data["tax_amount"] = clean_number(line)
        if "Gesamtwert inkl. MwSt." in line:
            data["gross_total"] = clean_number(line)

    # 7. Line items
    in_items = False
    for row in table:
        if not row or len(row) < 6:
            continue
        if any(k in str(c) for c in row for k in ["Pos.", "Artikelbeschreibung"]):
            in_items = True
            continue
        if not in_items:
            continue

        desc = str(row[1] or "").strip()
        if len(desc) < 3:
            continue

        qty = clean_number(row[3]) if len(row) > 3 else 1.0
        price = clean_number(row[4]) if len(row) > 4 else 0.0
        total = clean_number(row[5]) if len(row) > 5 else 0.0

        if total > 0:
            data["line_items"].append(LineItem(
                description=desc,
                quantity=qty,
                unit_price=price,
                line_total=total
            ))

    return Invoice.model_validate(data, strict=False)


def extract_from_folder(folder: Path) -> List[Invoice]:
    invoices = []
    for pdf_path in sorted(Path(folder).glob("*.pdf")):
        try:
            inv = extract_from_pdf(pdf_path)
            invoices.append(inv)
            print(f" {pdf_path.name} {inv.invoice_number} | Buyer: '{inv.buyer_name}' | Seller: '{inv.seller_name}'")
        except Exception as e:
            print(f"[ERROR] {pdf_path.name}: {e}")
    return invoices