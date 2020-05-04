#!/usr/bin/env python3
from pymongo import MongoClient
from pprint import pprint
import datetime
import numpy as np

client = MongoClient("mongodb+srv://mary_martin:If6was9then%3F@lp-cluster-jdvpa.mongodb.net/?authSource=admin")
db = client.Staffing

# server status command and results 
serverStatusResult=db.command("serverStatus")
# pprint(serverStatusResult)

def add_event(name, date, time, duration, evt_type, num_employees):
     
    event = {
        'event_name': name,
        'week_of': date,
        'time': time, 
        'duration': duration,
        'type': evt_type, 
        'num_employees': num_employees
    }
    db.Events.insert_one(event)
    print('event created: ', name)

def add_employee(name, can_manage, event_pref, availability):
    
    if(can_manage == 'N'):
        can_manage = False
    else:
        can_manage = True

    db.Available_hours.insert_one(availability)

    employee = {
        'name': name,
        'can_manage': can_manage,
        'event_pref': event_pref,
        'availability': availability
    }
    db.Employees.insert_one(employee)

    avai_id = availability['_id']
    employee = db.Employees.find_one({'name': name})
    db.Available_hours.update_one({'_id': avai_id},{'$set': {'employee_id': employee['_id']}})

    print('Employee added: ', name)
    print('Current availability: ', availability)

    
def set_availability(name, hrs):
    # update for each day of the week s
    employee = db.Employees.find_one({'name': name})
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
    db.employees.update_one({'name': employee.get('name')}, { '$set': { 'unavailability': availability } })
    db.Available_hours.insert_one(availability)
    print("Employee hours have been set.")
    print(availability)

def change_event_pref(name, pref):
    employee = db.Employees.find_one({'name': name})
    db.employees.update_one({'_id': employee.get('_id')}, { '$set': { 'event_pref': pref } })

def get_event(event_name):
    event = db.Events.find_one({'event_name': event_name})
    return event

def get_employee_list():
    employee_list = list(db.Employees.find({}))
    print("Employee list: ", employee_list)
    return employee_list

def get_event_list():
    event_list = list(db.Events.find({}))
    print("Event list: ", event_list)
    return event_list

def get_employee_count():
    employee_count = len(list(db.Events.find({})))
    print("Employee count: ", employee_count)
    return employee_count

def staff_event(event_name):
    event = get_event(event_name)
    hr = int(event['time'][:2])
    if hr < 2:
        slot = 9
    elif hr < 4:
        slot = 10
    elif hr < 6:
        slot = 11
    elif hr < 8:
        slot = 0
    elif hr < 10:
        slot = 1
    elif hr < 12:
        slot = 2
    elif hr < 14:
        slot = 3
    elif hr < 16:
        slot = 4
    elif hr < 18:
        slot = 5
    elif hr < 20:
        slot = 6
    elif hr <22:
        slot = 7
    else:
        slot = 8
    
    week_of = event['week_of']
    month, day, year = (int(x) for x in week_of.split('/'))    
    ans = datetime.date(year, month, day)
    d_week = ["Sunday", "Monday", "Tuesday", "Wednesday","Thursday","Friday","Saturday"]
    # print("=============================================================================")
    # print(ans)
    day_i = d_week.index(ans.strftime("%A"))
    numStaff = event['num_employees']
    staffs = get_employee_list()
    
    i = 0
    while i < len(numStaff):
        for s in staffs:
            avail = []
            avai = s['availability']
            avail.append(np.array(avai["Sunday"]).astype(int))
            avail.append(np.array(avai["Monday"]).astype(int))
            avail.append(np.array(avai["Tuesday"]).astype(int))
            avail.append(np.array(avai["Wednesday"]).astype(int))
            avail.append(np.array(avai["Thursday"]).astype(int))
            avail.append(np.array(avai["Friday"]).astype(int))
            avail.append(np.array(avai["Saturday"]).astype(int))
            print("=============================================================================")
            print(slot, day_i, np.shape(avail))
            if s['event_pref'] == event['type'] or s['event_pref'] == "No Preference":
                
                if avail[day_i][slot] == 1 and i <=len(numStaff)+1:
                    i += 1
                    print(s['name'])
                    # db.staff_event(s, event_name)
                    add_field = "staff"+str(i)
                    db.Events.update_one({'_id':  event.get('_id')  }, { '$set': { add_field: s} })

# def update_weekly_hours(employee_id, week_of, hrs):
#     hrs_td = db.Weekly_hours.find_one({'employee_id': employee_id, 'week_of': week_of})
#     total = hrs_td['hours']
#     _id = hrs_td['_id']
#     db.Weekly_hours.update_one({'_id': _id},{'$set': {'hours': (total+hrs)}})

# def get_availability(day, employee_id):
#     availability = db.Available_hours.find_one({'employee_id': employee_id})
#     print(availability)
#     print(day)
#     return availability[str(day)]

