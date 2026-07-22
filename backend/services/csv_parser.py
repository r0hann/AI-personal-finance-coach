import pandas as pd
from io import BytesIO
from datetime import date
from typing import List
from models.transaction import Transaction


# Common column name mappings across bank CSV exports
_DATE_COLS = {"date", "transaction date", "posted date", "trans. date", "value date"}
_DESC_COLS = {
    "description",
    "memo",
    "details",
    "narrative",
    "transaction",
    "payee",
    "merchant name",
}
_AMOUNT_COLS = {"amount", "debit", "credit", "transaction amount"}


def _find_col(columns: list[str], candidates: set[str]) -> str | None:
    normalized = {c.lower().strip(): c for c in columns}
    for cand in candidates:
        if cand in normalized:
            return normalized[cand]
    return None


def parse_csv(file_bytes: bytes) -> List[Transaction]:
    df = pd.read_csv(BytesIO(file_bytes))
    df.columns = [c.strip() for c in df.columns]

    date_col = _find_col(df.columns.tolist(), _DATE_COLS)
    desc_col = _find_col(df.columns.tolist(), _DESC_COLS)
    amount_col = _find_col(df.columns.tolist(), _AMOUNT_COLS)

    if not date_col or not desc_col or not amount_col:
        missing = []
        if not date_col:
            missing.append("date")
        if not desc_col:
            missing.append("description")
        if not amount_col:
            missing.append("amount")
        raise ValueError(
            f"CSV missing required columns: {', '.join(missing)}. "
            f"Found: {', '.join(df.columns.tolist())}"
        )

    transactions: List[Transaction] = []
    for _, row in df.iterrows():
        try:
            parsed_date = pd.to_datetime(row[date_col]).date()
            amount = float(
                str(row[amount_col]).replace(",", "").replace("$", "").strip()
            )
            desc = str(row[desc_col]).strip()
            if not desc or pd.isna(row[desc_col]):
                continue

            transactions.append(
                Transaction(
                    date=parsed_date,
                    description=desc,
                    amount=amount,
                    raw_csv_row=row.to_dict(),
                )
            )
        except (ValueError, TypeError):
            continue

    return transactions
