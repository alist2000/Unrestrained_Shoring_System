import numpy as np
import plotly.graph_objects as go
from scipy.integrate import quad, cumulative_trapezoid
from scipy.optimize import fsolve
from math import atan, sin, cos, pi


# --- 1. Surcharge Calculation Engine (Based on user's provided formulas) ---

def get_surcharge_pressure_point(x, H, q, l):
    """Calculates lateral pressure (psf) at depth x from a point load."""
    if x < 1e-9: return 0
    m = l / H
    n = x / H
    if m <= 0.4:
        sigma_h = 0.28 * q * (n ** 2) / ((H ** 2) * (0.16 + n ** 2) ** 3)
    else:
        sigma_h = 1.77 * q * (m ** 2) * (n ** 2) / ((H ** 2) * (m ** 2 + n ** 2) ** 3)
    return sigma_h


def get_surcharge_pressure_line(x, H, q, l):
    """Calculates lateral pressure (psf) at depth x from a line load."""
    if x < 1e-9: return 0
    m = l / H
    n = x / H
    if m <= 0.4:
        sigma_h = 0.2 * q * n / (H * (0.16 + n ** 2) ** 2)
    else:
        sigma_h = 1.28 * q * (m ** 2) * n / (H * (m ** 2 + n ** 2) ** 2)
    return sigma_h


def get_surcharge_pressure_strip(x, H, q, l1, l2):
    """Calculates lateral pressure (psf) at depth x from a strip load."""
    if x < 1e-9: return 0
    beta = atan(l2 / x) - atan(l1 / x)
    alpha = atan((l1 + l2) / (2 * x))
    sigma_h = (q / pi) * (2 * beta - sin(2 * beta) * cos(2 * alpha))
    return sigma_h


def get_total_surcharge_pressure(x, H, all_surcharges):
    """Calculates the total lateral pressure (psf) at depth x from all surcharges."""
    total_pressure = 0
    for load in all_surcharges:
        if load['type'] == 'uniform':
            total_pressure += load.get('q', 0)
        elif load['type'] == 'point':
            total_pressure += get_surcharge_pressure_point(x, H, load.get('q', 0), load.get('l', 0))
        elif load['type'] == 'line':
            total_pressure += get_surcharge_pressure_line(x, H, load.get('q', 0), load.get('l', 0))
        elif load['type'] == 'strip':
            total_pressure += get_surcharge_pressure_strip(x, H, load.get('q', 0), load.get('l1', 0), load.get('l2', 0))
    return total_pressure


# =============================================================================
# Function: Cantilever Pile Design (Compute Factored Embedment Depth D)
# =============================================================================
def cantilever_pile_design(H, EFPa, EFPp, surcharges, FS=1.3, spacing=8.0):
    """
    Design a cantilever soldier pile based on moment equilibrium using a numerical solver
    to handle complex surcharge loads.
    """

    def moment_equilibrium(D):
        if D <= 0: return 1e6  # Return a large error for non-physical depths

        # Driving Moment from Surcharge (using numerical integration)
        surcharge_moment_integrand = lambda x: get_total_surcharge_pressure(x, H, surcharges) * spacing * (H + D - x)
        M_surcharge = quad(surcharge_moment_integrand, 0, H)[0]

        # Driving Moment from Active Pressure
        P_active = 0.5 * EFPa * (H + D) ** 2 * spacing
        M_active = P_active * (H + D) / 3.0
        MDR = M_surcharge + M_active

        # Resisting Moment from Passive Pressure
        P_passive = 0.5 * EFPp * D ** 2 * spacing
        MRS = P_passive * D / 3.0

        return FS * MDR - MRS

    # Solve for the depth D where the moment equilibrium function is zero
    D_required, = fsolve(moment_equilibrium, x0=H)
    return D_required


# =============================================================================
# Function: Cantilever Pile Analysis (Shear, Moment, and Deflection)
# =============================================================================
def cantilever_pile_analysis(H, D0, EFPa, EFPp, surcharges, spacing=8.0,
                             Ix=1830, E=29000, Sx=154, A=20.1, fy=50.0):
    """
    Analyze the cantilever pile using unfactored depth D0.
    Returns shear, moment, and deflection diagrams.
    """
    total_depth = H + D0
    dx = 0.01
    x_vals = np.arange(0, total_depth + dx, dx)

    # --- Define Net Pressure Distribution ---
    def get_net_pressure(x):
        surcharge_force = get_total_surcharge_pressure(x, H, surcharges) * spacing
        active_force = EFPa * x * spacing
        passive_force = EFPp * (x - H) * spacing if x > H else 0
        return surcharge_force + active_force - passive_force

    net_pressure_vals = np.array([get_net_pressure(x) for x in x_vals])  # in lb/ft

    # --- Compute Shear & Moment Diagrams by Numerical Integration ---
    V_vals = cumulative_trapezoid(net_pressure_vals, x_vals, initial=0)  # in lbs
    M_vals = cumulative_trapezoid(V_vals, x_vals, initial=0)  # in lb-ft

    # --- Flexural Rigidity ---
    EI = E * 1000 * Ix  # lb-in^2

    # --- Deflection Calculation using Moment-Area Method (Delta-C Approach) ---
    # This section is kept exactly as per the user's original logic.
    B = H + 3
    E_pt = total_depth
    C = (B + E_pt) / 2

    iB = np.argmin(np.abs(x_vals - B))
    iC = np.argmin(np.abs(x_vals - C))

    sum_C = 0.0
    for j in range(iB + 1, iC + 1):
        sum_C += M_vals[j] * dx * (x_vals[iC] - x_vals[j])
    delC = sum_C * (12 ** 3) / EI

    v_profile = np.zeros_like(x_vals)
    for i, x in enumerate(x_vals):
        if x <= B:
            sum_x = 0.0
            i_x = i
            for j in range(i_x, iB + 1):
                sum_x += M_vals[j] * dx * (x_vals[j] - x_vals[i_x])
            delta_xB = sum_x * (12 ** 3) / EI
            alpha = abs((B - x) / (B - C)) if (B - C) != 0 else 0
            v_profile[i] = delta_xB + alpha * delC
        else:
            v_profile[i] = 0.0

    top_deflection = v_profile[0]
    max_shear = max(abs(V_vals)) / 1000  # kips
    max_moment = max(abs(M_vals)) / 1000  # kips-ft
    max_deflection = max(abs(v_profile))  # inches

    # --- Plotting with Plotly ---
    fig_shear = go.Figure(data=go.Scatter(x=x_vals, y=V_vals / 1000, mode='lines', name='Shear', fill='tozeroy'))
    fig_shear.update_layout(title="Shear Diagram", xaxis_title="Depth (ft)", yaxis_title="Shear (kips)")

    fig_moment = go.Figure(data=go.Scatter(x=x_vals, y=M_vals / 1000, mode='lines', name='Moment', fill='tozeroy'))
    fig_moment.update_layout(title="Moment Diagram", xaxis_title="Depth (ft)", yaxis_title="Moment (kip-ft)")

    fig_defl = go.Figure()
    fig_defl.add_trace(go.Scatter(x=v_profile, y=x_vals, mode='lines', name='Deflected Shape', line=dict(color='red')))
    fig_defl.add_trace(go.Scatter(x=np.zeros_like(x_vals), y=x_vals, mode='lines', name='Original Shape',
                                  line=dict(color='black', dash='dash')))
    fig_defl.update_layout(title="Deflected Shape", xaxis_title="Lateral Deflection (in)", yaxis_title="Depth (ft)",
                           yaxis=dict(autorange="reversed"))

    import plotly.io as pio
    pio.renderers.default = 'browser'
    fig_shear.show()
    fig_moment.show()
    fig_defl.show()

    return {
        "max_shear": max_shear,
        "max_moment": max_moment,
        "top_deflection": top_deflection,
    }


# =============================================================================
# Example Usage (Combined)
# =============================================================================
if __name__ == "__main__":
    # Example input parameters
    H = 11.33  # ft
    EFPa = 30.0  # pcf
    EFPp = 320.0  # pcf
    FS = 1.3
    spacing = 8.0 # ft

    # Define advanced surcharges
    surcharges = [
        {'type': 'line', 'q': 2000, 'l': 7.67},
    ]

    # Section properties (example values)
    Ix = 2070.0
    E = 29000.0

    # Design: compute factored embedment depth D
    D_factored = cantilever_pile_design(H, EFPa, EFPp, surcharges, FS, spacing)
    # Analysis: compute unfactored embedment depth D0
    D_unfactored = cantilever_pile_design(H, EFPa, EFPp, surcharges, 1.0, spacing)

    print("\n=== Cantilever Pile Design ===")
    print(f"Required Embedment Depth, D: {D_factored:.3f} ft")
    print(f"Factored Embedment Depth, D_final: {1.2 * D_factored:.2f} ft")
    print(f"Unfactored Depth, D₀: {D_unfactored:.3f} ft")

    # Analysis: Use unfactored depth D0 for shear, moment, and deflection
    results = cantilever_pile_analysis(H, D_unfactored, EFPa, EFPp, surcharges, spacing, Ix, E)

    print("\n=== Analysis Results ===")
    print(f"Max Shear: {results['max_shear']:.3f} kips")
    print(f"Max Moment: {results['max_moment']:.3f} kips-ft")
    print(f"Top Deflection: {results['top_deflection']:.4f} in")
