# Employee Scheduling Tool Using Google OR-tools

## Package Needed 
(check more infomation in each .py file)
- Pymongo
- Tkinter
- GoogleOR-Tool
- xlsxwriter

## Instruction
- Download code to local
- Run from `gui.py` (frontend)
  - Window should pop up
  - If created export schedule (Excel will be made in the same folder)
  
## Project outline
- Add Employee
  - Name (Entry)
  - Senior Staff? (Y/N) (Spinner)
  - Event Type Preference (Spinner)
  - Availability (checkbox list)
- Add Event
  - Event Name (Entry)
  - Event Type (Spinner)
  - Date
  - Time
  - Duration
  - # Staff Need
- Staff an Event
  - Select Event (Spinner)
  - Staff Event (Button)
- Generate Schedule
  - Generate without fit availability (Button)
  - Generate with Employee's availability (Button)
- Export Data
  - Export Data: Events, Staffs (Button)
