import data as db
import sys
from ortools.sat.python import cp_model
import datetime
from random import randint

global EMPLOYEE_HOURLY_LIMIT
EMPLOYEE_HOURLY_LIMIT = 10

def schedule_week():
    # maximize based on preferred event type 
    # set solver to CP Solver
    model = cp_model.CpModel()

    # get specified events
    events = db.get_event_list()
    num_events = len(db.get_event_list())

    employees = db.get_employee_list()

    # 2 hr intervals starting at 6 am
    # event intervals
    shifts = {}
    event_preferences =  []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    all_managers = []
    all_avail = []

    for n, employee in enumerate(employees):
        employee_id = employee['_id']
        avail = []
        can_manage = []
        for e, event in enumerate(events):
            time = event['time']
            hours = float(time[0:2])
            mins = float(time[3:5])
            print('hours ', hours)
            start_time = hours + mins/60
            duration = float(event['duration'])
            end_time = start_time + duration
            week_of = event['week_of']

            time_slot = generate_time_slots(start_time, end_time)
            weekday = get_day_of_week(event['week_of'])
            duration = range(int(duration))
            print(employee_id)
            availability = db.get_availability(days[weekday], employee_id)
            event_pref = []
            can_manage = employee['can_manage']

            available = 1
            for n, slot in enumerate(time_slot):
                if slot == 1 and availability[n] == 0:
                    available = 0

            model.Add(available == 1)

            for h in duration:
                shifts[(n, e, h)] = model.NewBoolVar('eventshift_n%ie%ih%i' % (n, e))
                event_pref.append(pref)

            model.Add(sum(shifts[(n, e, h)] for h in duration) + db.get_weekly_hours(employee_id, week_of) <= EMPLOYEE_HOURLY_LIMIT)
        event_preferences.append(event_pref)

    for e, event in enumerate(events):
        model.Add(sum(shifts[(n, e, h)] for n in range(num_employees)) == event['num_employees'])
    
    model.Maximize(
        sum(event_preferences[n][e][h] * shifts[(n, e, h)] for n in range(num_employees) for e in num_employees for h in duration))

    solver.solve(model)
    show_solutions(solver, shifts, events, employees, duration, event_preferences)
    
def set_schedule(employees):
    db.staff_event(employees)

def show_solutions(shifts, events, employees, duration, event_pref):

    for n, employee in enumerate(employees):
        for e, event in enumerate(events):
            for h in duration: 
                if solver.Value(shifts[(n, e, h)]) == 1:
                    if event_pref[n][e][h] == 1:
                        print('Employee: ', employee['name'], 'Works event: ', event['event_name'], ' (preferred)')
                    else: 
                        print('Employee: ', employee['name'], 'Works event: ', event['event_name'], ' (not preferred)')
    return 

def get_day_of_week(date):
    month = int(date[0:2])
    day = date[3:5]
    year = date[6:10]
    return randint(0,6)


def generate_time_slots(start, end):
    day = [0] * 12

    time = 6.0
    for n in range(12):
        if start >= time and start < (time + 2):
            day[n] = 1
            i = n
        if end <=  (time + 2) and end > time:
            day[n] = 1
            j = n
        time += 2.0
        if time > 24:
            time = 0

    for n in range(12):
        if n > i and n < j:
            day[n] = 1
    print(day)
    return day 

        
