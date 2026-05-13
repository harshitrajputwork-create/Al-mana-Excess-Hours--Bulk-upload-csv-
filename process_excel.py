import pandas as pd
import numpy as np

file_path = r"C:\Users\Harshit Rajput\Downloads\Master Sheet -Fixed Assets Register-Majid-Laptop.xlsx"
out_path = r"C:\Users\Harshit Rajput\Downloads\Demo_Sample_Fixed_Assets.xlsx"

df = pd.read_excel(file_path)

# Calculate non-NA count for each row to prioritize complete data
df['non_na_count'] = df.notna().sum(axis=1)
df = df.sort_values(by='non_na_count', ascending=False)

selected_rows = []
branches = df['Branch'].unique()

for branch in branches:
    branch_df = df[df['Branch'] == branch]
    # Try to get different categories
    categories = branch_df['Catogory'].unique()
    
    branch_selection = []
    
    # First, pick one from each available category (up to 3 or 4)
    for cat in categories:
        cat_df = branch_df[branch_df['Catogory'] == cat]
        if not cat_df.empty:
            branch_selection.append(cat_df.iloc[0])
            
        if len(branch_selection) >= 3:
            break
            
    # If we still need more to reach 3, just pick remaining best rows
    if len(branch_selection) < 3:
        remaining = branch_df[~branch_df.index.isin([x.name for x in branch_selection])]
        for _, row in remaining.head(3 - len(branch_selection)).iterrows():
            branch_selection.append(row)
            
    selected_rows.extend(branch_selection)

final_df = pd.DataFrame(selected_rows)
# drop the temporary column
final_df = final_df.drop(columns=['non_na_count'])

# Save to the new excel file
final_df.to_excel(out_path, index=False)
print(f"Successfully saved {len(final_df)} rows to {out_path}")
