import sympy as sp
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.graph_objs import Layout


# =============================================================================
# Function: Cantilever Pile Design (Compute Factored Embedment Depth D)
# =============================================================================
def cantilever_pile_design(H, EFPa, EFPp, surcharge=0, FS=1.3, spacing=8.0, fy=50.0):
    """
    Design a cantilever soldier pile based on moment equilibrium.
    Uses the factored equilibrium (FS*MDR = MRS) to compute D.

    Parameters:
      H         : Retaining height (ft)
      EFPa      : Active pressure (psf) (e.g., 34*1.4142)
      EFPp      : Passive pressure (psf) (e.g., 250*1.4142)
      surcharge : Surcharge load (psf)
      FS        : Safety Factor
      spacing   : Pile spacing (ft)
      fy        : Steel yield stress (ksi) [unused here]

    Returns:
      D_req : Required embedment depth (ft, factored design)
    """
    D = sp.Symbol('D', real=True, positive=True)

    # Driving forces and moments:
    DR1 = surcharge * 10 * spacing  # surcharge force: surcharge * surcharge_depth; here surcharge_depth=10 ft
    R1 = D + (H - 5)
    DR2 = EFPa * H ** 2 / 2 * spacing
    R2 = D + H / 3
    DR3 = EFPa * H * D * spacing
    R3 = D / 2
    DR4 = EFPa * D ** 2 / 2 * spacing
    R4 = D / 3

    # Passive force and moment:
    RS1 = EFPp * D ** 2 / 2 * spacing
    S1 = D / 3

    MDR = DR1 * R1 + DR2 * R2 + DR3 * R3 + DR4 * R4  # Driving moment
    MRS = RS1 * S1  # Resisting moment

    eq = sp.Eq(FS * MDR, MRS)
    sols = sp.solve(eq, D, dict=True)
    D_candidates = [sol[D].evalf() for sol in sols if sol[D].is_real and sol[D].evalf() > 0]
    if not D_candidates:
        raise ValueError("No positive real solution for D. Check inputs.")
    # Choose smallest positive solution
    D_req = float(min(D_candidates))
    return D_req


# =============================================================================
# Function: Cantilever Pile Analysis (Shear, Moment, and Deflection)
# =============================================================================
def cantilever_pile_analysis(H, D0, EFPa, EFPp, surcharge=0, spacing=8.0,
                             Ix=1830, E=29000, Sx=154, A=20.1, fy=50.0):
    """
    Analyze the cantilever pile using unfactored depth D0.
    Returns shear, moment, and deflection diagrams.
    The deflection is computed using a moment–area method over the free portion
    (from the top to the fixed point) as follows:

      - Define B = PoF = H + 2 (point of fixity), E = H + D0 (pile end),
        and C = (B + E)/2.
      - Compute delta_C as the additional deflection contribution from B to C.
      - For each x in [0, B] (pile top to fixed point), compute delta_xB
        by integrating the moment diagram from x to B and add an extra term:
          defl(x) = delta_xB + alpha * (delta_C)
          where alpha = (B - x) / (C - B).
      - For x > B, the deflection is set to zero.

    Parameters:
      H        : Retaining height (ft)
      D0       : Unfactored embedment depth (ft)
      EFPa     : Active pressure (psf) (e.g., 34*1.4142)
      EFPp     : Passive pressure (psf) (e.g., 250*1.4142)
      surcharge: Surcharge load (psf)
      spacing  : Pile spacing (ft)
      Ix       : Moment of inertia (in^4)
      E        : Modulus of elasticity (ksi)
      Sx, A, fy: Other parameters for capacity checks (not used in deflection)

    Returns:
      A dictionary with maximum shear (kips), maximum moment (kips-ft),
      and the deflection profile (x (ft) vs. deflection (in)).
    """
    # Total pile length (ft)
    total_depth = H + D0
    # Create a vertical coordinate array (0 = top, total_depth = bottom)
    dx = 0.01  # ft
    x_vals = np.arange(0, total_depth + dx, dx)

    # --- Define Load Distribution and Compute Shear & Moment Diagrams ---
    # Here we mimic the MATLAB piecewise definitions.
    # For x from 0 to H (above embedment), active pressure and surcharge apply;
    # for x >= H, passive pressure is also included.
    V_vals = np.zeros_like(x_vals)
    M_vals = np.zeros_like(x_vals)
    # For shear due to surcharge, use DR1D = surcharge * spacing
    DR1D = surcharge * spacing
    Lsur = 0 + 0  # In this formulation, we assume surcharge is applied at top.
    # (You can modify Lsur if needed; the MATLAB code uses LDepth+arm.)

    # For active pressure, assume a linear distribution: q_active = EFPa * x (psf)
    # For passive pressure (in the embedment zone x >= H): q_passive = EFPp*(x - H)
    for i, x in enumerate(x_vals):
        if x <= H:
            # Only active (and surcharge) loads above H
            V_vals[i] = - (DR1D * x + EFPa * (x ** 2) / 2 * spacing)
            M_vals[i] = - (DR1D * (x ** 2) / 2 + EFPa * (x ** 2) / 2 * spacing * (x / 3))
        else:
            # For x >= H, add passive component
            V_vals[i] = - (DR1D * x + EFPa * (x ** 2) / 2 * spacing) - (- EFPp * ((x - H) ** 2) / 2 * spacing)
            # Here, passive acts in opposition so we add a positive term.
            M_vals[i] = - (DR1D * (x ** 2) / 2 + EFPa * (x ** 2) / 2 * spacing * (x / 3)) \
                        - (- EFPp * ((x - H) ** 2) / 2 * spacing * ((x - H) / 3))
    # (Signs and exact formulas may be adjusted to match your design convention.)

    # --- Flexural Rigidity ---
    # Convert E from ksi to psi: multiply by 1000.
    EI = E * 1000 * Ix  # lb-in^2

    # --- Deflection Calculation using Moment-Area Method (Delta-C Approach) ---
    # Define key points:
    B = H + 4  # Point of fixity (ft)
    print("B: ", B)
    E_pt = total_depth  # End of pile (ft)
    C = (B + E_pt) / 2  # Midpoint between B and E
    print("x_vals - b: ", x_vals - B)

    # Find indices in x_vals for B and C:
    iB = np.argmin(np.abs(x_vals - B))
    iC = np.argmin(np.abs(x_vals - C))

    # (a) Compute delta_C (deflection contribution from B to C)
    # MATLAB integration for delta-C:
    sum_C = 0.0
    # Integrate from B (index iB) to C (index iC)
    for j in range(iB + 1, iC + 1):
        # (x_vals[iC]-x_vals[iB]) is the total span BC; (j - iB)*dx is the distance from B.
        # sum_C += M_vals[j] * dx * ((x_vals[iC] - x_vals[iB]) - (j - iB) * dx)
        sum_C += M_vals[j] * dx * (x_vals[iC] - x_vals[j])
    # Multiply by a factor as in MATLAB:
    # delC = (H + 4) / (x_vals[iC] - x_vals[iB]) * sum_C * (12 ** 3) / EI
    delC = sum_C * (12 ** 3) / EI
    # delC is in inches.
    # (b) For each x from top (0) to B, compute deflection by integrating moment area
    v_profile = np.zeros_like(x_vals)
    for i, x in enumerate(x_vals):
        if x <= B:
            # Integrate from current x to B:
            sum_x = 0.0
            # Find index corresponding to current x:
            i_x = i
            for j in range(i_x, iB + 1):
                # My version
                sum_x += M_vals[j] * dx * (x_vals[j] - x_vals[i_x])
                # Dr version
                # sum_x += M_vals[j] * dx * (x_vals[iB] - x_vals[j])

                # print("M : ", M_vals[j] / 1000)
                # print("x difference: ", (x_vals[iB] - x_vals[j]))
            delta_xB = sum_x * (12 ** 3) / EI  # in inches
            # print(delta_xB)
            # Define alpha as (B - x)/(B - C)
            alpha = abs((B - x) / (B - C)) if (B - C) != 0 else 0
            # Total deflection at x:
            v_profile[i] = delta_xB + alpha * delC
        else:
            # For x > B (in fixed region) deflection is zero.
            v_profile[i] = 0.0

    # The top deflection is at x = 0:
    top_deflection = v_profile[0]

    # --- Capacity Checks (Optional) ---
    max_shear = max(abs(V_vals)) / 1000  # in kips
    max_moment = max(abs(M_vals)) / 1000  # in kips-ft
    max_deflection = max(abs(v_profile))  # in inches

    # --- Plotting with Plotly ---
    # Shear Diagram
    fig_shear = go.Figure()
    fig_shear.add_trace(go.Scatter(x=x_vals, y=V_vals, mode='lines', name='Shear'))
    fig_shear.update_layout(title="Shear Diagram", xaxis_title="Depth (ft)", yaxis_title="Shear (lb/ft)",
                            yaxis=dict(autorange="reversed"))

    # Moment Diagram
    fig_moment = go.Figure()
    fig_moment.add_trace(go.Scatter(x=x_vals, y=M_vals, mode='lines', name='Moment'))
    fig_moment.update_layout(title="Moment Diagram", xaxis_title="Depth (ft)", yaxis_title="Moment (ft-lb)",
                             yaxis=dict(autorange="reversed"))

    # Deflection Diagram (Moment-Area based)
    fig_defl = go.Figure()
    fig_defl.add_trace(go.Scatter(x=v_profile, y=x_vals, mode='lines+markers', name='Deflected Shape',
                                  line=dict(color='red', width=2)))
    # Plot the original (undeformed) shape (vertical line at zero deflection)
    fig_defl.add_trace(go.Scatter(x=np.zeros_like(x_vals), y=x_vals, mode='lines', name='Original Shape',
                                  line=dict(color='black', dash='dash')))
    fig_defl.update_layout(title="Cantilever Pile Deflected Shape (Moment-Area Method)",
                           xaxis_title="Lateral Deflection (inches)", yaxis_title="Depth (ft)",
                           yaxis=dict(autorange="reversed"))

    # Top Deflection Value Plot (single marker)
    fig_top_defl = go.Figure()
    fig_top_defl.add_trace(go.Scatter(x=[0], y=[top_deflection], mode='markers+text',
                                      text=[f"{top_deflection:.4f} in"],
                                      textposition="top center",
                                      marker=dict(size=10, color='blue'),
                                      name="Top Deflection"))
    fig_top_defl.update_layout(title="Top Pile Deflection (Moment-Area Method)",
                               xaxis_title="(Arbitrary)", yaxis_title="Deflection (inches)")

    # Display plots
    import plotly.io as pio
    pio.renderers.default = 'browser'
    fig_shear.show()
    fig_moment.show()
    fig_defl.show()
    fig_top_defl.show()

    # --- Print Key Results ---
    print("------------------------------------------------------")
    print("CANTILEVER PILE ANALYSIS RESULTS")
    print("------------------------------------------------------")
    print(f"Total Pile Length (H + D₀): {total_depth:.3f} ft")
    print(f"Point of Fixity, B: {B:.3f} ft")
    print(f"Midpoint, C: {C:.3f} ft")
    print(f"Top Deflection: {top_deflection:.4f} in")
    print("------------------------------------------------------")

    return {
        "max_shear": max_shear,
        "max_moment": max_moment,
        "max_deflection": max_deflection,
        "top_deflection": top_deflection,
        "deflection_profile": (x_vals, v_profile)
    }


# =============================================================================
# Example Usage (Combined)
# =============================================================================
if __name__ == "__main__":
    # Example input parameters
    H = 15  # ft
    EFPa = 30  # pcf
    EFPp = 320   # pcf
    surcharge = 0  # psf (if any)
    FS = 1.3
    spacing = 8.0  # ft
    fy = 50.0  # ksi

    # Section properties (example values)
    Ix = 3270.0
    A  = 27.6
    Sx = 243.0
    E  = 29000.0
    # Design: compute factored embedment depth D using factored equilibrium
    D_factored = cantilever_pile_design(H, EFPa, EFPp, surcharge, FS, spacing, fy)
    # Compute unfactored embedment depth D0 (by setting FS = 1 in design)
    D_unfactored = cantilever_pile_design(H, EFPa, EFPp, surcharge, 1.0, spacing, fy)

    print("\n=== Cantilever Pile Design ===")
    print(f"Required Embedment Depth, D: {D_factored:.3f} ft")
    print(f"Factored Embedment Depth, D: {1.2 * D_factored:.2f} ft")
    print(f"Unfactored Depth, D₀: {D_unfactored:.3f} ft")

    # Analysis: Use unfactored depth D0 for shear, moment, and deflection
    results = cantilever_pile_analysis(H, D_unfactored, EFPa, EFPp, surcharge, spacing, Ix, E, Sx, A, fy)

    print("\n=== Analysis Results ===")
    print(f"Max Shear: {results['max_shear']:.3f} kips")
    print(f"Max Moment: {results['max_moment']:.3f} kips-ft")
    print(f"Max Deflection (from profile): {results['max_deflection']:.4f} in")
    print(f"Top Deflection: {results['top_deflection']:.4f} in")
