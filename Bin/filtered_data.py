#!/usr/bin/env python3
import csv
import os
import sys
from collections import Counter

SRC = os.environ.get("ROLLBACK_CSV", "rollback_data.csv")
OUT = os.environ.get("OUT_CSV", "filtered_rollback_data.csv")

def norm(s):
    """Normalize for comparison: strip + case-insensitive; None stays None."""
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    s = s.strip()
    return s.casefold() if s else None

def strip_if_str(x):
    return x.strip() if isinstance(x, str) else x

# Inputs (only these two are used for filtering)
app_area_in = os.environ.get("App_Area", "")
ticket_in   = os.environ.get("Ticket", "")

app_area = norm(app_area_in)   # will be used as 'contains'
ticket   = norm(ticket_in)     # will be used as exact

# Guard: require at least one filter (so we don't return the entire CSV)
if app_area is None and ticket is None:
    print("ERROR: Provide at least one of Application_and_Area or Rollback_Ticket.", file=sys.stderr)
    sys.exit(2)

# Validate input file
if not os.path.isfile(SRC):
    print(f"ERROR: {SRC} not found. Nothing to filter.", file=sys.stderr)
    sys.exit(1)

total_rows = 0
filtered = []
headers_out = []

with open(SRC, "r", newline="", encoding="utf-8-sig") as f:  # utf-8-sig removes BOM
    reader = csv.DictReader(f)
    raw_headers = reader.fieldnames or []
    seen = set()
    for h in raw_headers:
        hn = h.strip()
        if hn and hn not in seen:
            headers_out.append(hn)
            seen.add(hn)

    missing_cols = [c for c in ["Application_and_Area", "Rollback_Ticket"] if c not in headers_out]
    if missing_cols:
        print(f"WARNING: Missing expected columns in CSV: {missing_cols}. "
              f"Headers seen: {headers_out}", file=sys.stderr)

    for row in reader:
        total_rows += 1
        row_norm = { (k.strip() if k else k): strip_if_str(v) for k, v in row.items() }

        # --- Contains match for Application_and_Area ---
        if app_area is not None:
            area_val = norm(row_norm.get("Application_and_Area"))
            if area_val is None or app_area not in area_val:
                continue

        # --- Exact match for Ticket ---
        if ticket is not None:
            ticket_val = norm(row_norm.get("Rollback_Ticket"))
            if ticket_val != ticket:
                continue

        filtered.append(row_norm)

# Write all original columns (post-strip)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    from csv import DictWriter
    writer = DictWriter(f, fieldnames=headers_out, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(filtered)

print(f"[INFO] Inputs → App_Area={app_area_in!r}, Ticket={ticket_in!r}")
print(f"[INFO] Scanned {total_rows} row(s); wrote {len(filtered)} row(s) to {OUT}")

if total_rows > 0 and len(filtered) == 0:
    sample_limit = 10
    areas = Counter()
    tickets = Counter()
    with open(SRC, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            areas[strip_if_str(row.get("Application_and_Area", ""))] += 1
            tickets[strip_if_str(row.get("Rollback_Ticket", ""))] += 1
    print("[HINT] No matches found.")
    print(" Examples of Application_and_Area values:", ", ".join([repr(k) for k, _ in areas.most_common(sample_limit)]))
    print(" Examples of Rollback_Ticket values     :", ", ".join([repr(k) for k, _ in tickets.most_common(sample_limit)]))
