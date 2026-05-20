# Employee Excess Hours Calculator

A Streamlit app that calculates cumulative excess or shortage hours for employees by combining an attendance export with a previous-month carry-forward.

## Inputs

| File | Description |
|------|-------------|
| **Attendance CSV** | Monthly attendance export containing employee email, store name, and deviation column (`Deviation (Over time / Under time)`) |
| **Process Dump CSV** | Previous month's output — used to carry forward the opening balance (`New Month - Excess or shortage hours`) |

## How to run

```bash
pip install streamlit pandas openpyxl
streamlit run streamlit_app.py
```

## Output

Downloads an `.xlsx` file with one row per employee/store combination:

| Column | Description |
|--------|-------------|
| Submission Date | Today's date |
| Store Name | Store the employee belongs to |
| User Email | Employee email |
| Last Month carry-forward | Opening balance from previous month |
| New Month Total overtime | Overtime accumulated this month |
| New Month Total undertime | Undertime accumulated this month |
| New Month Excess/Shortage | Net balance after carry-forward |
| Total is Excess or Shortage | `Excess` or `Shortage` label |

## Notes

- All time values are formatted as `H:MM` (e.g. `1:30` = 1 hour 30 min)
- Negative values indicate shortage; the label column makes this explicit
- Excel cells are forced to Text format to prevent auto-conversion of time strings
