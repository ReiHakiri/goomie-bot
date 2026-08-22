import datetime
import minizinc

def solve(file_name: str, solver: str) -> minizinc.Result:
    model = minizinc.Model(file_name)
    use_solver = minizinc.Solver.lookup(solver)
    instance = minizinc.Instance(use_solver, model)

    result = instance.solve(datetime.timedelta(minutes = 2))

    return result