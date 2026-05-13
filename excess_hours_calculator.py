import pandas as pd
import re
import argparse
from datetime import datetime

def parse_deviation(val):
    if pd.isna(val):
        return 0, 0
    m = re.search(r'(\d+)h (\d+)m - (undertime|overtime)', str(val), re.IGNORECASE)
    if m:
        h = int(m.group(1))
        mins = int(m.group(2))
        total_mins = h * 60 + mins
        if m.group(3).lower() == 'overtime':
            return total_mins, 0
        else:
            return 0, total_mins
    return 0, 0

def format_hm(total_mins):
    if total_mins == 0:
        return "00:00"
    sign = "-" if total_mins < 0 else ""
    total_mins = abs(int(total_mins))
    h = total_mins // 60
    m = total_mins % 60
    return f"{sign}{h:02d}:{m:02d}"

def process_excess_hours(attendance_path, opening_bucket_path, output_path):
    print(f"Processing Attendance: {attendance_path}")
    print(f"Processing Opening Bucket: {opening_bucket_path}")
    
    # 1. Read Attendance CSV
    df_att = pd.read_csv(attendance_path)
    
    # Extract overtime and undertime into minutes
    df_att[['Overtime_Mins', 'Undertime_Mins']] = df_att.apply(
        lambda row: pd.Series(parse_deviation(row.get('Deviation (Over time / Under time)'))), 
        axis=1
    )
    
    # Extract clean mappings
    df_att['Email'] = df_att['Email'].astype(str).str.strip()
    df_att['Name_Clean'] = df_att['Name'].astype(str).str.strip().str.lower()
    df_att['Emp_ID_Clean'] = df_att['Employee ID'].astype(str).str.strip()
    
    # Create mapping from Email to Name and Employee ID based on attendance data
    email_to_name = {}
    email_to_emp_id = {}
    for _, row in df_att.dropna(subset=['Email']).iterrows():
        email = row['Email']
        if pd.notna(row['Name']) and str(row['Name']).lower() != 'nan':
            email_to_name[email] = row['Name_Clean']
        if pd.notna(row['Employee ID']) and str(row['Employee ID']).lower() != 'nan':
            email_to_emp_id[email] = row['Emp_ID_Clean']
            
    # Group by Email and Store to aggregate times
    df_grouped = df_att.groupby(['Email', 'Store']).agg({
        'Overtime_Mins': 'sum',
        'Undertime_Mins': 'sum'
    }).reset_index()
    
    # 2. Read Opening Bucket
    # Assuming row 3 (0-indexed 2) has headers like in the GSNAS sample
    try:
        df_open = pd.read_excel(opening_bucket_path, header=3)
    except Exception as e:
        print(f"Error reading opening bucket. Trying without header offset: {e}")
        df_open = pd.read_excel(opening_bucket_path)
        
    col_mapping = {col: str(col).strip() for col in df_open.columns}
    df_open.rename(columns=col_mapping, inplace=True)
    
    # Find the opening balance column
    opening_balance_col = [col for col in df_open.columns if 'TOTAL EXCESS HOURS' in col and 'BEGINNING BALANCE' in col]
    if not opening_balance_col:
        # Fallback to 5th column if exact name not found
        if len(df_open.columns) > 4:
            opening_balance_col = df_open.columns[4]
        else:
            opening_balance_col = df_open.columns[-1]
    else:
        opening_balance_col = opening_balance_col[0]
        
    df_open_clean = df_open.dropna(subset=['Name', opening_balance_col], how='all')
    
    # Parse opening balances
    name_to_opening_mins = {}
    emp_id_to_opening_mins = {}
    
    for _, row in df_open_clean.iterrows():
        name = str(row.get('Name', '')).strip().lower()
        emp_id = str(row.get('Final Employee ID', row.get('Employee ID', ''))).strip()
        val = row.get(opening_balance_col, 0)
        
        try:
            mins = float(val) * 60
            if name and name != 'nan':
                name_to_opening_mins[name] = mins
            if emp_id and emp_id != 'nan':
                emp_id_to_opening_mins[emp_id] = mins
        except (ValueError, TypeError):
            pass
            
    # 3. Calculate final values
    # We use the current date or the max date from the attendance
    submission_date = datetime.today().strftime('%d-%m-%Y')
    
    results = []
    for _, row in df_grouped.iterrows():
        email = row['Email']
        store = str(row['Store']).strip()
        ot_mins = row['Overtime_Mins']
        ut_mins = row['Undertime_Mins']
        
        if email == 'nan':
            continue
            
        # Match opening balance by Employee ID first, then by Name
        name = email_to_name.get(email, "")
        emp_id = email_to_emp_id.get(email, "")
        
        opening_mins = 0
        if emp_id in emp_id_to_opening_mins:
            opening_mins = emp_id_to_opening_mins[emp_id]
        elif name in name_to_opening_mins:
            opening_mins = name_to_opening_mins[name]
            
        excess_mins = opening_mins + ot_mins - ut_mins
        
        results.append({
            'Submission Date': submission_date,
            'Store Name': store,
            'User Email': email,
            'Total overtime-0100002': format_hm(ot_mins),
            'Total undertime-0100003': format_hm(ut_mins),
            'Excess or shortage hours-0100004': format_hm(excess_mins)
        })
        
    df_out = pd.DataFrame(results)
    df_out.to_csv(output_path, index=False)
    print(f"\nSuccessfully generated {output_path}")
    print(f"Total records processed: {len(df_out)}")
    print(df_out.head())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process Employee Excess Hours')
    parser.add_argument('--attendance', type=str, default=r'C:\Users\Harshit Rajput\Downloads\Herfy V\Attendance_amfgsportsdiv (1).csv', help='Path to Attendance CSV')
    parser.add_argument('--opening', type=str, default=r'C:\Users\Harshit Rajput\Downloads\Herfy V\APRIL EXCESS HOURS-GSNAS.xlsx', help='Path to Opening Bucket Excel')
    parser.add_argument('--output', type=str, default=r'C:\Users\Harshit Rajput\Downloads\Herfy V\Final_Process_Bulk_Upload.csv', help='Path to Output CSV')
    
    args = parser.parse_args()
    process_excess_hours(args.attendance, args.opening, args.output)
