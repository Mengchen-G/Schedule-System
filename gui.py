#!/usr/bin/env python3
import tkinter as tk
import tkinter.ttk as ttk
import collections
import data as db
import numpy as np
import xlsxwriter
import schedule as schedule
import datetime

root = tk.Tk()
root.geometry("1000x600")

###############################
#     Add Employee Window
###############################
class Window_employee():
    def __init__(self):
        win1 = tk.Toplevel(root)
        self.win1 = win1
        win1.geometry("845x675-20-20")
        # title = tk.Label(win1, text="Add an employee",pady=50, bg="#B8BBC5",font=("Helvetica", 16),width = 920)
        title = tk.Label(win1, text="          Add an employee           ",pady=50, bg="#B8BBC5", font=("Helvetica", 16))
        title.grid(row=0, column=4)#.pack()
        blank1 = tk.Label(win1, text = "employee ", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
        blank2 = tk.Label(win1, text = "employee ", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
        blank3 = tk.Label(win1, text = "employee ", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
        blank4 = tk.Label(win1, text = "employee ", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
        blank5 = tk.Label(win1, text = "employee ", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
        blank6 = tk.Label(win1, text = "employee ", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
        blank7 = tk.Label(win1, text = "employee ", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
        blank8 = tk.Label(win1, text = "employee ", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
        blank1.grid(row=0, column=0)
        blank2.grid(row=0, column=1)
        blank3.grid(row=0, column=2)
        blank4.grid(row=0, column=3)
        blank5.grid(row=0, column=5)
        blank6.grid(row=0, column=6)
        blank7.grid(row=0, column=7)
        blank8.grid(row=0, column=8)

        tk.Label(win1, text="Name").grid(row=1, column=4)#.pack()
        self.name_entry = tk.Entry(win1, width = 20)
        self.name_entry.insert(0, "FirstName LastName")
        self.name_entry.grid(row=2, column=4)#.pack()

        tk.Label(win1, text="Senior Staff?").grid(row=3, column=4)#.pack()
        self.comboSenior = tk.ttk.Combobox(win1, values=["Y", "N"], width=18)
        self.comboSenior.grid(row=4, column=4)#.pack()
        
        tk.Label(win1, text="Choose Event Type Preference").grid(row=5, column=4)#.pack()
        self.comboEvent = tk.ttk.Combobox(win1, values=["Art", "Music", "Theater", "Reception", "Dance", "No Preference"], width=18)
        self.comboEvent.grid(row=6, column=4)#.pack()

        tk.Label(win1, text="Choose Availability").grid(row=8, column=4)#.pack()
        self.data = np.zeros((12, 7)).astype(int) #collections.defaultdict(list)
        self.colT = ["Sunday","Monday", "Tuesday", "Wednesday","Thursday","Friday","Saturday"]
        self.rowT = ["6-8 AM","8-10 AM","10-12 PM","12-2 PM","2-4 PM","4-6 PM","6-8 PM","8-10 PM","10-12 AM","12-2 AM","2-4 AM","4-6 AM"]

        rowrange = range(len(self.rowT))
        colrange = range(len(self.colT))

        #Create the grid labels
        for x in colrange:
            w = tk.Label(win1, text=self.colT[x])
            w.grid(row=9, column=x+1)

        for y in rowrange:
            w = tk.Label(win1, text=self.rowT[y])
            w.grid(row=y+10, column=0)

        #Create the Checkbuttons & save them for future reference
        self.grid = []
        for y in rowrange:
            row = []
            for x in colrange:
                b = tk.Checkbutton(win1)

                #Store the button's position and value as attributes
                b.pos = (y+10, x)
                b.var = tk.IntVar()

                #Create a callback bound to this button
                func = lambda w=b: self.check_cb(w)
                b.config(variable=b.var, command=func)
                b.grid(row=y+10, column=x+1)
                row.append(b)
            self.grid.append(row)
        # self.get_checked()

        #Track the number of on buttons in each row
        self.rowstate = len(self.rowT) * [0]

        self.up = tk.Button(win1, text="Update")
        self.up['command']= self.get_input#lambda:[self.get_input, self.get_checked]
        self.up.grid(row=22, column=8)#.pack()

    def get_input(self):
        name = self.name_entry.get()
        senior = self.comboSenior.get()
        event = self.comboEvent.get()

        i = 0
        for row in self.grid:
            for x,b in enumerate(row):
                if b.var.get() == 1: #and self.rowT[i] not in self.data[self.colT[x]]:
                    self.data[i, x] = 1 #self.data[self.colT[x]].append(self.rowT[i])
    
            i += 1
        hrs = self.data

        availability = {
        'employee_id': "",
        'Sunday': hrs[:, 0].tolist(),
        'Monday': hrs[:, 1].tolist(),
        'Tuesday': hrs[:, 2].tolist(),
        'Wednesday': hrs[:, 3].tolist(),
        'Thursday': hrs[:, 4].tolist(),
        'Friday': hrs[:, 5].tolist(),
        'Saturday': hrs[:, 6].tolist()
        }
        # db.set_availability(name, hrs)
        # print("check name",name)
        # db.find_avail(name)
        # print(hrs)
        db.add_employee(name, senior, event, availability)
        # db.find_avail(name)
        self.win1.destroy()
    
    def check_cb(self, button):
        ''' Checkbutton callback '''
        state = button.var.get()
        y, _ = button.pos

        #Get the row containing this button
        row = self.grid[y-10]

        if state == 1:
            self.rowstate[y-10] += 1 
            for b in row:
                if b.var.get() == 0:
                    b.config(state=tk.NORMAL)
        else:
            self.rowstate[y-10] -= 1 
            if self.rowstate[y-10] == 1:
                #Enable all currently off buttons in this row
                for b in row:
                    if b.var.get() == 0:
                        b.config(state=tk.NORMAL)



###############################
#          Add Event
###############################

class Window_event():
    def __init__(self):
        win2 = tk.Toplevel(root)
        win2.geometry("920x600+20+20")
        title = tk.Label(win2, text="Add an Event",pady=50, bg="#B8BBC5", font=("Helvetica", 16), width = 920)
        title.pack()

        tk.Label(win2, text="Enter Event Name").pack()
        self.nameField = tk.Entry(win2, width=22)
        self.nameField.pack()
        
        tk.Label(win2, text="Choose Event Type").pack()
        self.comboEvent = tk.ttk.Combobox(win2, values=["Art", "Music", "Theater", "Reception", "Dance", "No Preference"],width=22)
        self.comboEvent.pack()

        tk.Label(win2, text="Choose Event Date").pack()
        self.dateField = tk.Entry(win2, width=22)
        self.dateField.insert(0, "Format: mm/dd/yyyy")
        self.dateField.pack()

        tk.Label(win2, text="Choose Event Time").pack()
        self.timeField = tk.Entry(win2, width=22)
        self.timeField.insert(0, "Format: hh:mm (24 hrs)")
        self.timeField.pack()

        tk.Label(win2, text="Duration of Event (hr)").pack()
        self.comboDuration = tk.ttk.Combobox(win2, values=[i/2 for i in range(1,11)],width=22)
        self.comboDuration.pack()

        tk.Label(win2, text="# Staff Needed").pack()
        self.comboNumStaff = tk.ttk.Combobox(win2, values=[i for i in range(1,31)],width=22)
        self.comboNumStaff.pack()

        self.add_btn = tk.Button(win2, text="Add Event")
        self.add_btn['command']=self.get_input
        self.add_btn.pack()

    def get_input(self):
        eventName = self.nameField.get()
        eventType = self.comboEvent.get()
        date = self.dateField.get()
        time = self.timeField.get()
        duration = self.comboDuration.get()
        numStaff = self.comboNumStaff.get()
        eventInfo = [eventName, date, time, eventType, duration, numStaff]
        db.add_event(eventName, date, time, duration, eventType, numStaff)
        return eventInfo


###############################
#      Staff Event Window
###############################
class Window_staff():
    def __init__(self):
        win3 = tk.Toplevel(root)
        win3.geometry("920x600+20+20")
        title = tk.Label(win3, text="Staff an Event", bg="#B8BBC5",pady=50, font=("Helvetica", 16), width = 920)
        title.pack()
        tk.Label(win3, text="     ").pack()

        eventl = []
        timel = []
        events = db.get_event_list()
        for event in events:
            eventl.append(event['event_name'])

        tk.Label(win3, text="Find Event in Database").pack()
        self.combo_event = tk.ttk.Combobox(win3, values=eventl, width=20)
        self.combo_event.pack()


        tk.Label(win3, text="     ").pack()

        self.add_btn = tk.Button(win3, text="Staff Event")
        self.add_btn['command']=self.get_input
        self.add_btn.pack()

    def get_input(self):
        event_name=self.combo_event.get()
        event = db.get_event(event_name)
        
        print("=============================================================================")
        print(event)
        return event_name


###############################
#   Schedule Generate Window
###############################
class Window_generate():
    def __init__(self):
        win4 = tk.Toplevel(root)
        win4.geometry("920x600+20+20")
        title = tk.Label(win4, text="Generate Weekly Schedule", bg="#B8BBC5",pady=50, font=("Helvetica", 16), width=920)
        title.pack()

        tk.Label(win4, text="      ").pack()

        self.gen_btn1 = tk.Button(win4, text="Generate Schedule", command=self.get_input)
        self.gen_btn1.pack()
        tk.Label(win4, text="      ").pack()

        self.gen_btn2 = tk.Button(win4, text="Generate Schedule Based on Request", command=self.get_input2)
        self.gen_btn2.pack()

    def get_input(self):
        schedule.schedule_week()

    def get_input2(self):
        schedule.schedule_week_request()


###############################
#   Schedule Export Window
###############################
class Window_export():
    def __init__(self):
        win5 = tk.Toplevel(root)
        win5.geometry("920x600+20+20")
        title = tk.Label(win5, text="Export Employee & Event Data", bg="#B8BBC5",pady=50, font=("Helvetica", 16), width=920)
        title.pack()

        # tk.Label(win5, text="Type any Date of the Week").pack()
        # self.date_entry = tk.Entry(win5)
        # self.date_entry.insert(0, "Format: mm/dd/yyyy")
        # self.date_entry.pack()
        tk.Label(win5, text="           ").pack()
        self.gen_btn = tk.Button(win5, text="Generate & Export")
        self.gen_btn['command']=self.get_input
        self.gen_btn.pack()

    def get_input(self):
        # date_typed = self.date_entry.get()
        # print(date_typed)
        event_list = db.get_event_list()
        staff_list = db.get_employee_list()
        writexls_event(event_list)
        writexls_staff(staff_list)
        return event_list

# Export func
def writexls_event(export_list):
    workbook = xlsxwriter.Workbook('events.xlsx')
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1})

    # Adjust the column width.
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(1, 2, 15)
    worksheet.set_column(1, 3, 15)

    # Write some data headers.
    worksheet.write('A1', "ID", bold)
    worksheet.write('B1', "Event Name", bold)
    worksheet.write('C1', 'Week Of', bold)
    worksheet.write('D1', 'Time', bold)
    worksheet.write('E1', 'Duration', bold)
    worksheet.write('F1', 'Type', bold)
    worksheet.write('G1', '# Staff Needed', bold)

    # Start from the first cell below the headers.
    row = 1
    col = 0

    # print(export_list)
    for i in range(len(export_list)):
        event = export_list[i]
        worksheet.write_number(row, col, i )  
        worksheet.write_string(row, col+1, event['event_name'] )  
        worksheet.write_string(row, col+2, event['week_of'] )  
        worksheet.write_string(row, col+3, event['time'] )  
        worksheet.write_string(row, col+4, event['duration'] ) 
        worksheet.write_string(row, col+5, event['type'] )   
        worksheet.write_string(row, col+6, event['num_employees'] )  
        row += 1
    print("Event Schedule Export Successfully")
    workbook.close()

# export func for staff
def writexls_staff(export_list):
    workbook = xlsxwriter.Workbook('staffs.xlsx')
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1})

    # Adjust the column width.
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(1, 2, 15)
    worksheet.set_column(1, 3, 15)

    # Write some data headers.
    worksheet.write('A1', "ID", bold)
    worksheet.write('B1', "Employee Name", bold)
    worksheet.write('C1', 'Senior Staff?', bold)
    worksheet.write('D1', 'Event Preference', bold)
    # worksheet.write('E1', 'Availability', bold)

    # Start from the first cell below the headers.
    row = 1
    col = 0

    # print(export_list)
    for i in range(len(export_list)):
        staff = export_list[i]
        worksheet.write_number(row, col, i )  
        worksheet.write_string(row, col+1, staff['name'] )  
        worksheet.write_string(row, col+2, "True" if(staff['can_manage']) else "False" )  
        worksheet.write_string(row, col+3, staff['event_pref'] )   
        # worksheet.write(row, col+4, staff['availability'])
        row += 1
    print("Staff List Export Successfully")
    workbook.close()


###############################
#         Root Window
###############################
# create label widge
welcome_label = tk.Label(text = "Employee Schedule System", pady=50, bg="#B8BBC5", font=("Helvetica", 16))
blank1 = tk.Label(text = "Employee Schedule System", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
blank2 = tk.Label(text = "Employee Schedule System", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
blank3 = tk.Label(text = "Employee Schedule System", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
blank4 = tk.Label(text = "Employee Schedule System", pady=50, fg="#B8BBC5", bg="#B8BBC5",font=("Helvetica", 16))
 
# create buttons
add_employee_btn = tk.Button(text="Add an Employee", height = 6)
add_event_btn = tk.Button(text="Add an Event", height = 6)
staff_event_btn = tk.Button(text="Staff an Event", height = 6)
create_schedule_btn = tk.Button(text="Create Weekly Schedule", height = 6)
export_schedule_btn = tk.Button(text="Export Employee/Event Data", height = 6)

# change buttons size
add_employee_btn.config(width=20)
add_event_btn.config(width=20)
staff_event_btn.config(width=20)
create_schedule_btn.config(width=20)
export_schedule_btn.config(width=20)

# layout in the window
blank1.grid(row=0, column=0)
blank2.grid(row=0, column=1)
blank3.grid(row=0, column=3)
blank4.grid(row=0, column=4)
welcome_label.grid(row=0, column=2)
add_employee_btn.grid(row=1, column=0)
add_event_btn.grid(row=1, column=1)
staff_event_btn.grid(row=1, column=2)
create_schedule_btn.grid(row=1, column=3)
export_schedule_btn.grid(row=1, column=4)


# click functions
add_employee_btn['command'] = Window_employee
add_event_btn['command'] = Window_event
staff_event_btn['command'] = Window_staff
create_schedule_btn['command'] = Window_generate
export_schedule_btn['command'] = Window_export

# print("main loop", userInfo, eventInfo)

root.mainloop()

    