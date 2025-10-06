from plotly.graph_objs import Layout

import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Layout
def cantilever_pile_design(H, EFPa, EFPp, surcharge=0, FS=1.3, spacing=1.0, fy=36.0, unit_system='us',
                           surcharge_depth=10):
    """
    Design a cantilever soldier pile based on bottom reference for arms and forces.

    Parameters:
    H : float
        Retaining height (ft or m)
    EFPa : float
        Effective active pressure coefficient (per unit height)
    EFPp : float
        Effective passive pressure coefficient (per unit height)
    surcharge : float
        Surcharge load at the top (uniform load per unit area)
    FS : float
        Factor of Safety
    spacing : float
        Pile spacing (ft or m)
    fy : float
        Steel yield stress (ksi or MPa)
    unit_system : str
        Units: 'us' (imperial) or 'metric'

    Returns:
    D : float
        Required embedment depth
    """

    # Symbol for embedment depth
    D = sp.Symbol('D', real=True, positive=True)

    # 1. Calculate active force and moment
    Fa = 0.5 * EFPa * (H + D) ** 2 * spacing  # Active force
    Ma = Fa * ((D + H) / 3.0)  # Moment arm from the bottom of active zone

    # 2. Calculate surcharge force and moment
    Fsurcharge = surcharge * surcharge_depth * spacing  # Total surcharge force
    Msurcharge = Fsurcharge * (D + H - (surcharge_depth / 2.0)) if surcharge else 0  # Moment arm for surcharge

    # 3. Calculate passive force and moment (in terms of D)
    Fp = 0.5 * EFPp * D ** 2 * spacing  # Passive force
    Mp = Fp * (D / 3.0)  # Moment arm for passive force

    # 4. Set up equilibrium equation
    eq = Mp - FS * (Ma + Msurcharge)  # Passive resistance must equal driving forces
    print("\n=== Equation Setup ===")
    print(f"Mp: {Mp}, Ma: {Ma}, Msurcharge: {Msurcharge}")
    print(f"Equilibrium Equation: {eq}")

    # 5. Solve for D
    solutions = sp.solve(eq, D)
    print("\n=== Solutions for D ===")
    print(f"Solutions: {solutions}")

    # Filter for positive real solutions
    D_sol = [sol for sol in solutions if sol.is_real and sol > 0]
    if not D_sol:
        raise ValueError("No positive real solution for D found. Check your inputs.")

    # Select the smallest valid D
    D_req = float(min(D_sol))
    print(f"Selected Embedment Depth (D): {D_req}")

    return D_req


import sympy as sp
import numpy as np
import plotly.graph_objects as go


def cantilever_pile_analysis(H, D, EFPa, EFPp, surcharge=0, spacing=1.0, Ix=500, E=29000, Sx=154.0, A=20.1, Fy=50.0):
    """
    Analyze the pile for shear, moment, and deflection diagrams and check shear and moment capacity.

    Parameters:
    H : float
        Retaining height (ft)
    D : float
        Embedment depth (ft)
    EFPa : float
        Effective active pressure coefficient (psf/ft)
    EFPp : float
        Effective passive pressure coefficient (psf/ft)
    surcharge : float
        Uniform surcharge load (psf)
    spacing : float
        Pile spacing (ft)
    Ix : float
        Moment of inertia (in^4)
    E : float
        Modulus of elasticity (ksi)
    Sx : float
        Section modulus (in^3)
    A : float
        Cross-sectional area (in^2)
    Fy : float
        Steel yield stress (ksi)
    """
    # Total depth of the pile
    total_depth = H + D
    z = sp.Symbol('z', real=True, positive=True)

    # 1. Define load distribution
    q_active = EFPa * spacing * z  # Active pressure increases linearly downward
    q_passive = EFPp * spacing * (z - H)  # Passive pressure increases upward
    q_surcharge = surcharge * spacing if surcharge else 0

    # Piecewise definition of the total load
    q_total = sp.Piecewise(
        (-q_active - q_surcharge, z <= H),  # Active pressure and surcharge above embedment depth
        (-q_active + q_passive, z > H)  # Add passive pressure in the embedded depth
    )

    # 2. Calculate Shear Force (V)
    u = sp.Symbol('u')  # Dummy variable for integration
    V = sp.Piecewise(
        (sp.integrate(q_total.subs(z, u), (u, 0, z)), z <= H),
        (
            sp.integrate(q_total.subs(z, u), (u, 0, H)) +
            sp.integrate(q_total.subs(z, u), (u, H, z)),
            z > H
        )
    )

    # 3. Calculate Moment (M)
    M = sp.Piecewise(
        (sp.integrate(V.subs(z, u), (u, 0, z)), z <= H),
        (
            sp.integrate(V.subs(z, u), (u, 0, H)) +
            sp.integrate(V.subs(z, u), (u, H, z)),
            z > H
        )
    )

    # 4. Calculate Deflection (w)
    # Integrate M / (E * Ix) twice and apply boundary conditions
    C1, C2 = sp.symbols('C1 C2')  # Constants of integration
    EI = E * Ix  # Flexural rigidity

    slope = sp.integrate(M / EI, z) + C1
    deflection = sp.integrate(slope, z) + C2

    # Apply boundary conditions at z = total_depth:
    # 1. Deflection = 0
    # 2. Slope = 0
    eq1 = deflection.subs(z, total_depth)
    eq2 = slope.subs(z, total_depth)

    constants = sp.solve([eq1, eq2], (C1, C2))
    slope = slope.subs(constants)
    deflection = deflection.subs(constants)

    # 5. Numerical Evaluation
    z_vals = np.linspace(0, total_depth, 500)

    def evaluate_piecewise(expr, z_vals):
        # Separate the piecewise parts
        conditions = expr.args
        results = []
        for z_val in z_vals:
            for condition in conditions:
                if condition[1].subs(z, z_val):  # Substitute z_val into the condition
                    results.append(condition[0].subs(z, z_val))  # Evaluate the expression
                    break
        return np.array(results, dtype=float)

    shear_vals = evaluate_piecewise(V, z_vals)
    moment_vals = evaluate_piecewise(M, z_vals)
    deflection_vals = [deflection.subs(z, zi) for zi in z_vals]
    deflection_vals = np.array(deflection_vals, dtype=float)

    # 6. Find Maximum Values
    max_shear = max(abs(shear_vals)) / 1000
    max_moment = max(abs(moment_vals)) / 1000
    max_deflection = max(abs(deflection_vals))

    # 7. Capacity Checks
    fv = max_shear / A  # Shear stress
    fv_max = 0.44 * Fy  # Allowable shear stress

    fb = max_moment * 12 / Sx  # Bending stress
    fb_max = 0.66 * Fy  # Allowable bending stress

    shear_status = "Satisfactory" if fv <= fv_max else "Not Satisfactory"
    moment_status = "Satisfactory" if fb <= fb_max else "Not Satisfactory"

    print("\n=== Section Checks ===")
    print(f"Shear Stress (fv): {fv:.2f} ksi")
    print(f"Allowable Shear Stress (fv_max): {fv_max:.2f} ksi")
    print(f"Shear Check: {shear_status}")
    print(f"Bending Stress (fb): {fb:.2f} ksi")
    print(f"Allowable Bending Stress (fb_max): {fb_max:.2f} ksi")
    print(f"Moment Check: {moment_status}")

    # 8. Plot Diagrams using Plotly

    # Load Diagram
    load_vals_active = [-EFPa * zi for zi in z_vals]
    load_vals_passive = [EFPp * (zi - H) if zi > H else 0 for zi in z_vals]

    fig = go.Figure()

    # Active Pressure
    fig.add_trace(go.Scatter(
        x=load_vals_active, y=z_vals, mode='lines',
        name='Active Pressure', line=dict(color='red')
    ))

    # Passive Pressure
    fig.add_trace(go.Scatter(
        x=load_vals_passive, y=z_vals, mode='lines',
        name='Passive Pressure', line=dict(color='orange')
    ))

    fig.update_yaxes(autorange='reversed')
    fig.update_layout(
        title="Load Diagram",
        xaxis_title="q (lb/ft)",
        yaxis_title="Depth z (ft)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )
    # fig.show()

    # Shear Diagram
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=shear_vals, y=z_vals, mode='lines',
        name='Shear Force', line=dict(color='blue')
    ))

    fig.update_yaxes(autorange='reversed')
    fig.update_layout(
        title="Shear Diagram",
        xaxis_title="Shear V (kips)",
        yaxis_title="Depth z (ft)"
    )
    # fig.show()

    # Moment Diagram
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=moment_vals, y=z_vals, mode='lines',
        name='Moment', line=dict(color='green')
    ))

    fig.update_yaxes(autorange='reversed')
    fig.update_layout(
        title="Moment Diagram",
        xaxis_title="Moment M (kips-ft)",
        yaxis_title="Depth z (ft)"
    )
    # fig.show()
    # Shear Diagram
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(
    #     x=deflection_vals, y=z_vals, mode='lines',
    #     name='Deflection', line=dict(color='blue')
    # ))
    #
    # fig.update_yaxes(autorange='reversed')
    fig.update_layout(
        title="Deflection Diagram",
        xaxis_title="Deflection (in)",
        yaxis_title="Depth z (ft)"
    )
    fig = px.line(x=deflection_vals, y=z_vals, color_discrete_sequence=["#595959"]).update_layout(
        title="Deflection Diagram",
        xaxis_title="Deflection (in)",
        yaxis_title="Depth z (ft)",
        xaxis={"side": "top", "tickfont": {"size": 16},
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True, "tickfont": {"size": 16},
               "mirror": "ticks",
               "zerolinecolor": "#969696",
               "zerolinewidth": 4}
    )
    fig['layout']['yaxis']['autorange'] = "reversed"
    layout = Layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )
    fig.update_layout(layout)

    fig.show()

    # Return key results
    return {
        "max_shear": max_shear,
        "max_moment": max_moment,
        "max_deflection": max_deflection,
        "shear_status": shear_status,
        "moment_status": moment_status
    }


# Combined Example Usage
# H = 25.0  # Retaining height
# EFPa = 31.0  # Effective active pressure coefficient
# EFPp = 600.0  # Effective passive pressure coefficient
surcharge = 0  # Uniform surcharge load
# FS = 1.3  # Factor of Safety
# spacing = 8.0  # Pile spacing
# fy = 50  # Steel yield stress
# Ix = 1830.0 * 2   # Moment of inertia (in^4)
# A = 20.1 * 2   # Cross-sectional area (in^2)
# Sx = 154 * 2   # Cross-sectional area (in^3)
# E = 29000.0  # Modulus of elasticity (ksi)
# Example inputs
# H = 13.5  # ft
# EFPa = 34  # psf/ft
# EFPp = 250.0  # psf/ft
# FS = 1.3
# spacing = 8.0  # ft
# fy = 50.0  # ksi
# Ix = 3000.0  # in^4
# A = 30.3  # in^2
# Sx = 245  # in^3
# E = 29000.0  # ksi
# #41 to 56
# H = 16.5
# EFPa = 46.0
# EFPp = 250.0
# FS   = 1.3
# spacing = 8
# fy = 50.0
# Ix = 4760.0
# A  = 27.6
# Sx = 345.0
# E  = 29000.0

#30 to 40
# H = 14
# EFPa = 35.0
# EFPp = 250.0
# FS   = 1.3
# spacing = 8
# fy = 50.0
# Ix = 1550.0
# A  = 18.2
# Sx = 131.0
# E  = 29000.0

#6 to 10
# H = 16.5
# EFPa = 35.0
# EFPp = 250.0
# FS   = 1.3
# spacing = 8
# fy = 50.0
# Ix = 2850.0
# A  = 24.7
# Sx = 213
# E  = 29000.0

##5 & #11 to #13 & #16 to #24 & #27
H = 15.5
EFPa = 35.0
EFPp = 250.0
FS   = 1.3
spacing = 8
fy = 50.0
Ix = 2850.0
A  = 24.7
Sx = 213
E  = 29000.0

##1 to #4 & #14 & #15 & #25 & #26 & #28 & #29
# H = 15
# EFPa = 35.0
# EFPp = 250.0
# FS   = 1.3
# spacing = 8
# fy = 50.0
# Ix = 2100.0
# A  = 23.9
# Sx = 176
# E  = 29000.0

# #6 to 10
# H = 16.5
# EFPa = 35.0
# EFPp = 250.0
# FS   = 1.3
# spacing = 8
# fy = 50.0
# Ix = 2700.0
# A  = 27.7
# Sx = 222
# E  = 29000.0
try:
    print("\n=== Cantilever Soldier Pile Design ===")
    D = cantilever_pile_design(H, EFPa, EFPp, surcharge, FS, spacing, fy)
    D0 = cantilever_pile_design(H, EFPa, EFPp, surcharge, 1, spacing, fy)
    results = cantilever_pile_analysis(H, D0, EFPa, EFPp, surcharge, spacing, Ix, E, Sx, A, fy)
    results2 = cantilever_pile_analysis(H, 4, EFPa, EFPp, surcharge, spacing, Ix, E, Sx, A, fy)
    print("\n=== Results ===")
    print(f"Required Embedment Depth: D = {D:.2f} ft")
    print(f"Final Embedment Depth: D = {1.2 * D:.2f} ft")
    print(f"Max Shear: {results['max_shear']} kips")
    print(f"Max Moment: {results['max_moment']} kips-ft")
    print(f"Max Deflection: {results2['max_deflection']} in")
    # cantilever_pile_analysis(H + D, EFPa, EFPp, Ix, A, spacing)
except ValueError as e:
    print("Error:", e)
