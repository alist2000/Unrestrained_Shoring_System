from sympy import symbols
from sympy.solvers import solve
from sympy import diff

from shoring_cantilever import control_solution


class lagging_design:
    def __init__(self, unit_system, L, section, ph, timber_size):
        self.unit_system = unit_system
        self.L = L
        self.section = section
        self.ph = ph
        self.timber_size = timber_size

    def moment_design(self, Fb):
        unit_system = self.unit_system
        l = self.L
        section = self.section
        ph = self.ph
        timber_size = self.timber_size

        # calculate diameter of concrete if our pile was w section
        # w of section
        x = section.find("X")
        w = float(section[1:x])
        if w <= 24:
            if unit_system == "us":
                d_concrete = 2  # ft
            else:
                d_concrete = 0.6096  # m
        if 24 < w <= 30:
            if unit_system == "us":
                d_concrete = 2.5  # ft
            else:
                d_concrete = 0.762  # m
        if 30 < w <= 36:
            if unit_system == "us":
                d_concrete = 3  # ft
            else:
                d_concrete = 0.9144  # m

        if 36 < w <= 42:
            if unit_system == "us":
                d_concrete = 3.5  # ft
            else:
                d_concrete = 1.0668  # m
        if 42 < w <= 48:
            if unit_system == "us":
                d_concrete = 4  # ft
            else:
                d_concrete = 1.2192  # m

        # calculate Lc
        lc = l - d_concrete

        # calculate R (reaction in piles)
        R = (ph * lc / 2) / 2

        x = symbols("x")
        # moment equation
        M = R * x - (ph / (lc / 2)) * pow(x, 3) / 6
        V = diff(M, x)
        v_zero = solve(V, x)
        v_zero = control_solution(v_zero)
        M_max = M.subs(x, v_zero)  # this is not exactly true! CHECK REPORT!
        return M_max, v_zero


test = lagging_design("us", 8, "W22X126", 400, "3X12")
M = test.moment_design(845)
