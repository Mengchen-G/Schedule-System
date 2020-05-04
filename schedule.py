import data as db
import numpy as np
import sys
from ortools.sat.python import cp_model
import datetime
import xlsxwriter

###########################################
#   weekly schedule no employee request
###########################################
class Schedule_week_print(cp_model.CpSolverSolutionCallback):
    def __init__(self, shifts, num_employees, num_days, num_shifts, sol):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._num_employees = num_employees
        self._num_days = num_days
        self._num_shifts = num_shifts
        self._solutions = set(sol)
        self._solution_count = 0

    def on_solution_callback(self):
        if self._solution_count in self._solutions:
            print('Solution %i' % self._solution_count)
            for d in range(self._num_days):
                print('Day %i' % d)
                for n in range(self._num_employees):
                    is_working = False
                    for s in range(self._num_shifts):
                        if self.Value(self._shifts[(n, d, s)]):
                            is_working = True
                            print('  Employee %i works shift %i' % (n, s))
                    if not is_working:
                        print('  Employee {} does not work'.format(n))
            print()
        self._solution_count += 1

    def solution_count(self):
        return self._solution_count

def schedule_week():
    employees = db.get_employee_list()
    num_employees = len(employees)
    num_shifts = 12
    num_days = 7
    all_employees = range(num_employees)
    all_shifts = range(num_shifts)
    all_days = range(num_days)

    # Creates the model.
    model = cp_model.CpModel()

    shifts = {}
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(e, d, s)] = model.NewBoolVar('shift_e%id%is%i' % (e, d, s))
    
    # each shift assigned to exactly 1 employee
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(e, d, s)] for e in all_employees) == 1)

    # Each employee works at most 4 shifts per day.
    for n in all_employees:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 4)

    # some employee need to take extra hous
    min_shifts_per_e = (num_shifts * num_days) // num_employees
    max_shifts_per_e = min_shifts_per_e + 1
    for n in all_employees:
        num_shifts_worked = sum(
            shifts[(e, d, s)] for d in all_days for s in all_shifts)
        model.Add(min_shifts_per_e <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_e)
    
    # create solver
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level=0

    # show solutions
    a_few_solutions = range(2)
    solution_printer = Schedule_week_print(shifts, 
                                           num_employees,
                                           num_days, 
                                           num_shifts,
                                           a_few_solutions)
    solver.SearchForAllSolutions(model, solution_printer)

    # Statistics.
    print()
    print('Statistics')
    print('  - conflicts       : %i' % solver.NumConflicts())
    print('  - branches        : %i' % solver.NumBranches())
    print('  - wall time       : %f s' % solver.WallTime())
    print('  - solutions found : %i' % solution_printer.solution_count())

###########################################
# weekly schedule based on employee request
###########################################
def schedule_week_request():
    employees = db.get_employee_list()
    num_employees = len(employees)
    num_shifts = 12
    num_days = 7
    all_employees = range(num_employees)
    all_shifts = range(num_shifts)
    all_days = range(num_days)

    shift_requests = []
    for employee in employees:
        avai = employee['availability']
        # print("change type ",np.array(avai["Sunday"]).astype(int))
        shift_requests.append([np.array(avai["Sunday"]).astype(int),
                               np.array(avai["Monday"]).astype(int),
                               np.array(avai["Tuesday"]).astype(int),
                               np.array(avai["Wednesday"]).astype(int),
                               np.array(avai["Thursday"]).astype(int),
                               np.array(avai["Friday"]).astype(int),
                               np.array(avai["Saturday"]).astype(int)])
    
    model = cp_model.CpModel()

    # shifts[(e, d, s)]: employee 'n' works shift 's' on day 'd'.
    shifts = {}
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(e, d, s)] = model.NewBoolVar('shift_e%id%is%i' % (e, d, s))
    
    # each shift assigned to exactly 1 employee
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(e, d, s)] for e in all_employees) == 1)
    
    # each employee can take max 4 shifts a day
    for e in all_employees:
        for d in all_days:
            model.Add(sum(shifts[(e, d, s)] for s in all_shifts) <= 4)
    
    min_shifts_per_e = (num_shifts * num_days) // num_employees
    max_shifts_per_e = min_shifts_per_e + 1
    for e in all_employees:
        num_shifts_worked = sum(
            shifts[(e, d, s)] for d in all_days for s in all_shifts)
        model.Add(min_shifts_per_e <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_e)

    model.Maximize(
        sum(shift_requests[e][d][s] * shifts[(e, d, s)] for e in all_employees
            for d in all_days for s in all_shifts))

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)
    export_list = []

    for d in all_days:
        print('Generating schedule for Day ', d)
        dlist = []
        dlist.append(d)
        for s in all_shifts:
            for e in all_employees:
                if solver.Value(shifts[(e, d, s)]) == 1:
                    if shift_requests[e][d][s] == 1:
                        # print('Employee', e, 'works shift', s, '(requested).')
                        dlist.append(str(e)+' (requested)')
                    else:
                        # print('employee', e, 'works shift', s, '(not requested).') 
                        dlist.append(str(e)+' (not requested)')

        export_list.append(dlist) 
        print()

    writexls(export_list)

    # Statistics.
    print()
    print('Statistics')
    print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
          '(out of', num_shifts * num_days, ')')
    print('  - wall time       : %f s' % solver.WallTime())


# Export Weekly Schedule based on availability
def writexls(export_list):
    workbook = xlsxwriter.Workbook('schedule_request1.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(1, 2, 15)
    worksheet.set_column(1, 3, 15)
    worksheet.set_column(1, 4, 15)
    worksheet.set_column(1, 5, 15)
    worksheet.set_column(1, 6, 15)
    worksheet.set_column(1, 7, 15)
    worksheet.set_column(1, 8, 15)
    worksheet.set_column(1, 9, 15)
    worksheet.set_column(1, 10, 15)
    worksheet.set_column(1, 11, 15)
    worksheet.set_column(1, 12, 15)
    worksheet.set_column(1, 13, 15)
    bold = workbook.add_format({'bold': 1})

    rowT = ["6-8 AM","8-10 AM","10-12 PM","12-2 PM","2-4 PM","4-6 PM","6-8 PM","8-10 PM","10-12 AM","12-2 AM","2-4 AM","4-6 AM"]

    # Write some data headers.
    worksheet.write('A1', "Day", bold)
    worksheet.write('B1', rowT[0], bold)
    worksheet.write('C1', rowT[1], bold)
    worksheet.write('D1', rowT[2], bold)
    worksheet.write('E1', rowT[3], bold)
    worksheet.write('F1', rowT[4], bold)
    worksheet.write('G1', rowT[5], bold)
    worksheet.write('H1', rowT[6], bold)
    worksheet.write('I1', rowT[7], bold)
    worksheet.write('J1', rowT[8], bold)
    worksheet.write('K1', rowT[9], bold)
    worksheet.write('L1', rowT[10], bold)
    worksheet.write('M1', rowT[11], bold)

    # Start from the first cell below the headers.
    row = 1
    for i in range(len(export_list)):
        worksheet.write_number(row, 0, export_list[i][0] ) 
        for j in range (1,len(export_list[0])):
            worksheet.write_string(row, j, export_list[i][j]) 
        row += 1
    print("Schedule based on Employee Request Export Successfully")
    workbook.close()