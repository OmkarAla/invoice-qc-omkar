# invoice_qc/cli.py
import typer
import json
from pathlib import Path
from rich import print as rprint
from rich.table import Table
from .extractor import extract_from_folder
from .validator import validate_invoices, print_validation_report

app = typer.Typer(help="Invoice QC Tool — Extract & Validate SUPEDIO Bestellungen")


@app.command()
def extract(pdf_dir: Path = Path("sample_pdfs"), output: Path = Path("extracted.json")):
    """Extract invoices from PDFs"""
    typer.echo("Extracting invoices...")
    invoices = extract_from_folder(pdf_dir)
    
    # FIXED LINE — serialize to JSON string
    output.write_text(json.dumps([inv.model_dump() for inv in invoices], indent=2, ensure_ascii=False), encoding="utf-8")
    
    rprint(f"[green]Extracted {len(invoices)} invoices → {output}[/green]")


@app.command()
def validate(json_path: Path = Path("extracted.json")):
    """Validate extracted invoices"""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    from .schema import Invoice
    invoices = [Invoice.model_validate(d) for d in data]
    results = validate_invoices(invoices)
    print_validation_report(results)


@app.command()
def full(pdf_dir: Path = Path("sample_pdfs")):
    """Extract + Validate in one go"""
    typer.echo("Running full pipeline...")
    invoices = extract_from_folder(pdf_dir)
    results = validate_invoices(invoices)
    print_validation_report(results)

    table = Table(title="Invoice QC Summary")
    table.add_column("File", style="cyan")
    table.add_column("Number", style="magenta")
    table.add_column("Buyer", max_width=30)
    table.add_column("Seller", max_width=25)
    table.add_column("Amount", justify="right")
    table.add_column("Status", justify="center")

    for r in results:
        status = "[green]VALID[/]" if r.is_valid else "[red]INVALID[/]"
        table.add_row(
            Path(r.invoice.source_file or "").name,
            r.invoice.invoice_number,
            r.invoice.buyer_name,
            r.invoice.seller_name,
            f"€{r.invoice.gross_total:,.2f}",
            status
        )

    rprint(table)


if __name__ == "__main__":
    app()