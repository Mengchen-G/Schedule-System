import data as db
import numpy as np
import sys
from ortools.sat.python import cp_model
import datetime
from random import randint


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
    num_shifts = 3
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

    # Each employee works at most 3 shifts per day.
    for n in all_employees:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 3)

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
    num_shifts = 3
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
    shifts = {}
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(e, d, s)] = model.NewBoolVar('shift_e%id%is%i' % (e, d, s))
    
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(e, d, s)] for e in all_employees) == 1)
    
    for e in all_employees:
        for d in all_days:
            model.Add(sum(shifts[(e, d, s)] for s in all_shifts) <= 3)
    
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
    for d in all_days:
        print('Day', d)
        for e in all_employees:
            for s in all_shifts:
                if solver.Value(shifts[(e, d, s)]) == 1:
                    if shift_requests[e][d][s] == 1:
                        print('Employee', e, 'works shift', s, '(requested).')
                    else:
                        print('employee', e, 'works shift', s, '(not requested).')
        print()
    
    # Statistics.
    print()
    print('Statistics')
    print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
          '(out of', num_employees * min_shifts_per_e, ')')
    print('  - wall time       : %f s' % solver.WallTime())

