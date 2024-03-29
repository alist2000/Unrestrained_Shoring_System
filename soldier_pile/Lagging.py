from sympy import symbols
from sympy.solvers import solve
from sympy import diff

from shoring_cantilever import control_solution
from database import SQL_reader_timber


class lagging_design:
    def __init__(self, unit_system, L, section, ph, timber_size):
        self.unit_system = unit_system
        self.L = L
        self.section = section
        self.ph = ph
        self.timber_size = timber_size

    def moment_design(self, Fb, tw, a_coef=1, b_coef=1, c_coef=1, d_coef=1, e_coef=1, f_coef=1):
        """a, b , ... f are coefficient for wood if user don't input them assume one"""
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
        # check M edited -> is it necessary to use tw of section. or we can assume.
        M_edited = R * (x + ((d_concrete - tw) / 2)) - (ph / (lc / 2)) * pow(x,
                                                                             3) / 6  # for 2 ft -> 0.75 ft according to report/ formula is my guess! must be qualified.
        M_max = M_edited.subs(x, v_zero)  # this is not exactly true! CHECK REPORT!

        # calculate S required
        if unit_system == "us":
            # M unit: lb-ft. should be: lb-in
            s_req = 12 * M_max / (Fb * 1000)  # check
        else:
            # M unit: N-m. should be: N-mm
            s_req = 1000 * M_max / Fb

        # import section
        b, h = SQL_reader_timber(timber_size, unit_system).values()

        # calculate s supplied
        s_sup = (a_coef * b_coef * c_coef * d_coef * e_coef * f_coef) * h * pow(b,
                                                                                2) / 6

        DCR_moment_timber = s_req / s_sup
        if DCR_moment_timber <= 1:
            status = "Pass"
        else:
            status = "Fail"
            # status = "Fail! Your timber fail in moment design."

        if unit_system == "us":
            d_concrete_edited = d_concrete * 12  # inch for output
        else:
            d_concrete_edited = d_concrete * 1000  # mm for output

        return DCR_moment_timber, status, d_concrete_edited, lc, R, M_max, s_req, s_sup

    # *** shear design function must be developed! ***
    def shear_design(self, v, Q, I, t):
        unit_system = self.unit_system
        ta = v * Q / (I * t)
        return ta

# test = lagging_design("us", 8, "W22X126", 400, "3 x 16")
# M = test.moment_design(845)
