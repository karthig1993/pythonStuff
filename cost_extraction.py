import pandas as pd
from pathlib import Path

# ---------------- CONFIGURATION ----------------
INPUT_FOLDER = "cost_sheets"          # Folder with CSV files
OUTPUT_FILE = "services_sorted.xlsx"  # Output Excel
# ----------------------------------------------

results = []

for file in Path(INPUT_FOLDER).glob("*.csv"):
    try:
        # Read CSV
        df = pd.read_csv(file)

        # Take the last row (totals row)
        totals_row = df.iloc[-1]

        # Convert to numeric (coerce non-numeric if needed)
        totals_numeric = pd.to_numeric(totals_row, errors='coerce')

        # Sort services from most expensive to least expensive
        sorted_services = totals_numeric.sort_values(ascending=False)

        # Append each service to results
        for service, cost in sorted_services.items():
            results.append({
                "File Name": file.name,
                "Service Name": service,
                "Total Cost": cost
            })

    except Exception as e:
        print(f"Skipping {file.name}: {e}")

# Create output DataFrame
output_df = pd.DataFrame(results)

# Write to Excel
output_df.to_excel(OUTPUT_FILE, index=False)

print(f"Output written to {OUTPUT_FILE}")
