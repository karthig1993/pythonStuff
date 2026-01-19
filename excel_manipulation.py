import pandas as pd
import os

folder_path = "cost_sheets"

for file_name in os.listdir(folder_path):
    if not file_name.lower().endswith(".csv"):
        continue

    file_path = os.path.join(folder_path, file_name)

    try:
        # Read CSV without headers
        df = pd.read_csv(file_path, header=None)

        # Find row containing 'Service Total' (case-insensitive)
        mask = df.apply(
            lambda row: row.astype(str)
            .str.contains("service total", case=False, na=False)
            .any(),
            axis=1
        )

        if not mask.any():
            print(f"'Service Total' not found in {file_name}")
            continue

        # Extract the Service Total row
        service_total_row = df[mask]

        # Remove it from original position
        df_remaining = df[~mask]

        # Append Service Total row to bottom
        df_final = pd.concat(
            [df_remaining, service_total_row],
            ignore_index=True
        )

        # --- Remove the last column ---
        df_final = df_final.iloc[:, :-1]

        # Write back to same file
        df_final.to_csv(
            file_path,
            index=False,
            header=False
        )

        print(f"Moved Service Total row and removed last column in: {file_name}")

    except Exception as e:
        print(f"Failed: {file_name} → {e}") 
print("n\nAll files processed.")
