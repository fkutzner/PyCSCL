import abc
import ctypes
import cscl.interfaces


class IPASIRSatSolver(cscl.interfaces.SatSolver, abc.ABC):
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

    def __enter__(self) -> cscl.interfaces.SatSolver:
        class IPASIRSatSolverImpl(IPASIRSatSolver):
            def __init__(self, path_to_solver_dso):
                self.dso = ctypes.CDLL(path_to_solver_dso)

                self.dso.ipasir_init.restype = ctypes.c_void_p
                self.dso.ipasir_release.argtypes = [ctypes.c_void_p]
                self.dso.ipasir_add.argtypes = [ctypes.c_void_p, ctypes.c_int]
                self.dso.ipasir_assume.argtypes = [ctypes.c_void_p, ctypes.c_int]
                self.dso.ipasir_solve.argtypes = [ctypes.c_void_p]
                self.dso.ipasir_solve.restype = ctypes.c_int
                self.dso.ipasir_val.argtypes = [ctypes.c_void_p, ctypes.c_int]
                self.dso.ipasir_val.restype = ctypes.c_int
                self.dso.ipasir_failed.argtypes = [ctypes.c_void_p, ctypes.c_int]
                self.dso.ipasir_failed.restype = ctypes.c_int

                self.solver = self.dso.ipasir_init()
                self.num_vars = 0

            def __del__(self):
                self.destroy()

            def consume_clause(self, clause):
                for lit in clause:
                    self.dso.ipasir_add(self.solver, lit)
                self.dso.ipasir_add(self.solver, 0)

            def create_literal(self):
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
                if self.solver is not None:
                    self.solver = None
                    self.dso.ipasir_release(self.solver)

        self.sat_solver = IPASIRSatSolverImpl(self.__path_to_solver_dso)
        return self.sat_solver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sat_solver.destroy()
