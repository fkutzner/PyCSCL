import abc
from ctypes import *
from cscl.interfaces import *


class IPASIRSatSolver(SatSolver, abc.ABC):
    """Interface for SAT solvers implementing the IPASIR interface"""
    pass


class IPASIRSatSolverResource:
    """
    Resource for IPASIR SAT solvers, with automatic cleanup. Use as follows:


    with IPASIRSatSolverResource(path_to_ipasir_dso) as solver:
        # solver is an IPASIRSatSolver object
        [... solve interesting problems with solver ...]


    path_to_ipasir_dso needs to be the path to the IPASIR solver's shared library.
    """

    def __init__(self, path_to_solver_dso):
        self.__path_to_solver_dso = path_to_solver_dso

    def __enter__(self) -> SatSolver:
        class IPASIRSatSolverImpl(IPASIRSatSolver):
            def __init__(self, path_to_solver_dso):
                self.dso = CDLL(path_to_solver_dso)

                self.dso.ipasir_init.restype = c_void_p
                self.dso.ipasir_release.argtypes = [c_void_p]
                self.dso.ipasir_add.argtypes = [c_void_p, c_int]
                self.dso.ipasir_assume.argtypes = [c_void_p, c_int]
                self.dso.ipasir_solve.argtypes = [c_void_p]
                self.dso.ipasir_solve.restype = c_int
                self.dso.ipasir_val.argtypes = [c_void_p, c_int]
                self.dso.ipasir_val.restype = c_int
                self.dso.ipasir_failed.argtypes = [c_void_p, c_int]
                self.dso.ipasir_failed.restype = c_int

                self.solver = self.dso.ipasir_init()
                self.num_vars = 0

            def __del__(self):
                if self.solver is not None:
                    self.dso.ipasir_release(self.solver)

            def consume_clause(self, clause):
                for lit in clause:
                    self.dso.ipasir_add(self.solver, lit)
                self.dso.ipasir_add(self.solver, 0)

            def create_variable(self):
                self.num_vars += 1
                return self.num_vars

            def solve(self, assumptions):
                for lit in assumptions:
                    self.dso.ipasir_assume(self.solver, lit)
                return self.dso.ipasir_solve(self.solver)

            def get_assignment(self, var):
                ipasir_assignment = self.dso.ipasir_val(self.solver, var)
                if ipasir_assignment == 0:
                    return None
                else:
                    return True if ipasir_assignment > 0 else False

            def destroy(self):
                self.dso.ipasir_release(self.solver)
                self.solver = None

        self.sat_solver = IPASIRSatSolverImpl(self.__path_to_solver_dso)
        return self.sat_solver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sat_solver.destroy()

