import sympy as sp
import numpy as np
import plotly.graph_objects as go

# -------------------------------------------------------------------
# 1) Cantilever Pile DESIGN (net passive = FS * net active)
# -------------------------------------------------------------------
def cantilever_pile_design(H, EFPa, EFPp, surcharge=0,
                           FS=1.3, spacing=1.0, fy=36.0,
                           surcharge_depth=10):
    """
    Classical net passive = FS * net active approach.
    Returns D_req (embedment).
    """
    D = sp.Symbol('D', real=True, positive=True)

    # Active force & moment
    Fa = 0.5 * EFPa * (H + D)**2 * spacing
    Ma = Fa * ((H + D)/3.0)

    # Surcharge force & moment
    Fsurch = surcharge * surcharge_depth * spacing
    Msurch = Fsurch * ((H + D) - (surcharge_depth/2.0)) if surcharge else 0

    # Passive force & moment
    Fp = 0.5 * EFPp * D**2 * spacing
    Mp = Fp * (D/3.0)

    # Solve Mp = FS*(Ma + Msurch)
    eq = Mp - FS*(Ma + Msurch)
    sol = sp.solve(eq, D)
    D_sol = [s for s in sol if s.is_real and s>0]
    if not D_sol:
        raise ValueError("No positive real solution for D.")
    return float(min(D_sol))


# -------------------------------------------------------------------
# 2) TWO-SEGMENT ANALYSIS (Shear, Moment, Deflection)
# -------------------------------------------------------------------
def cantilever_pile_analysis_two_segment(H, D, EFPa, EFPp,
                                         surcharge=0, spacing=1.0,
                                         Ix=500, E=29000, Sx=154.0, A=20.1, Fy=50.0):
    """
    Two-segment approach:
      Segment 1: z in [0, H]   (retained zone)
      Segment 2: z in [H, H+D] (embedded zone)

    We'll build symbolic expressions for Shear, Moment, Slope, Deflection in each segment:
      V1(z), M1(z), theta1(z), delta1(z) for 0<=z<=H
      V2(z), M2(z), theta2(z), delta2(z) for H<=z<=H+D

    Then apply boundary conditions:
      1) V1(0) = 0, M1(0) = 0      (free at top)
      2) continuity at z=H => M1(H)=M2(H), V1(H)=V2(H)
      3) delta2(H+D) = 0, slope2(H+D)=0  (fully fixed at tip)

    That set of 6 conditions solves for the 6 integration constants we will have
    (3 in each segment's M or slope? Actually it will be 2 for M in each segment + 2 for deflection in each segment = 8).
    We'll see how to reduce it carefully below.

    Returns a dict with arrays for z, shear, moment, deflection, plus max values, etc.
    """

    # 1) Symbolic variable and piecewise load
    z = sp.Symbol('z', real=True, nonnegative=True)
    total_depth = H + D

    # "q_active" for 0..H, plus surcharge
    # "q_passive" for H..H+D
    # We'll define them as piecewise so we can keep the same z domain:
    q_active = EFPa * spacing * z
    q_surch  = surcharge * spacing
    q_passive = EFPp * spacing * (z - H)

    # We'll define q1(z) for Segment 1 (0..H):
    q1 = -(q_active + q_surch)  # negative to the left
    # We'll define q2(z) for Segment 2 (H..H+D):
    q2 = -(q_active) + q_passive  # at z>H, active + passive

    # ----------------------------------------------------------------
    # SEGMENT 1:  0 <= z <= H
    # Shear1'(z) = q1(z).  We'll define M1'(z) = V1(z).
    # We do indefinite integrals and then apply boundary conditions.
    # ----------------------------------------------------------------
    # Define symbols for integration constants in segment1:
    C1v, C2m = sp.symbols('C1v C2m', real=True)  # one for shear->M, one for M-> ?

    # V1(z) = Integral of q1 dz + A constant.  But we want V1'(z)= q1 => V1(z)= ∫ q1 dz + c1
    # Then M1(z)= ∫ V1 dz + c2
    # We'll do it in one pass:

    # (1) Integrate q1 => V1_expr
    V1_expr = sp.integrate(q1, (z, 0, z)) + C1v  # definite integral from 0..z plus constant

    # (2) Integrate V1 => M1_expr
    M1_expr = sp.integrate(V1_expr, (z, 0, z)) + C2m

    # Boundary conditions for Segment 1 at z=0 (top free):
    #   V1(0)=0 => that yields an equation => V1_expr.subs(z,0)=0
    #   M1(0)=0 => M1_expr.subs(z,0)=0
    eq_s1 = [
        sp.Eq(V1_expr.subs(z, 0), 0),
        sp.Eq(M1_expr.subs(z, 0), 0)
    ]
    # Solve them:
    sol_s1 = sp.solve(eq_s1, (C1v, C2m), dict=True)
    if not sol_s1:
        raise ValueError("No solution for segment1 boundary conditions.")
    c1v_sol = sol_s1[0][C1v]
    c2m_sol = sol_s1[0][C2m]

    # Substitute them back:
    V1_expr = V1_expr.subs({C1v: c1v_sol, C2m: c2m_sol})
    M1_expr = M1_expr.subs({C1v: c1v_sol, C2m: c2m_sol})

    # ----------------------------------------------------------------
    # SEGMENT 2: H <= z <= H+D
    # We'll shift z so that integrals start at H for convenience.
    # Let x = z - H in [0..D].
    # q2 is function of z, so we can just do integrals w.r.t. x from 0..(z-H).
    # We'll define new constants for segment2: C3v, C4m.
    # Then we must enforce continuity:  V2(H)= V1(H), M2(H)= M1(H).
    # ----------------------------------------------------------------
    x = sp.Symbol('x', real=True, nonnegative=True)  # x= z-H
    C3v, C4m = sp.symbols('C3v C4m', real=True)

    # define q2 in terms of x => q2(H+x)
    q2_x = q2.subs(z, H + x)

    # V2(x) = ∫ q2_x dx from 0..x plus C3v
    V2_expr_x = sp.integrate(q2_x, (x, 0, x)) + C3v

    # M2(x) = ∫ V2_expr_x dx + C4m
    M2_expr_x = sp.integrate(V2_expr_x, (x, 0, x)) + C4m

    # We want continuity at x=0 => z=H
    #   V2(0) == V1(H), M2(0)== M1(H)
    eq_s2_cont = [
        sp.Eq(V2_expr_x.subs(x,0), V1_expr.subs(z,H)),
        sp.Eq(M2_expr_x.subs(x,0), M1_expr.subs(z,H))
    ]

    # We'll solve for C3v, C4m:
    sol_s2 = sp.solve(eq_s2_cont, (C3v, C4m), dict=True)
    if not sol_s2:
        raise ValueError("No solution for continuity at z=H.")
    c3v_sol = sol_s2[0][C3v]
    c4m_sol = sol_s2[0][C4m]

    # Final expressions for V2, M2:
    V2_expr_x = V2_expr_x.subs({C3v:c3v_sol, C4m:c4m_sol})
    M2_expr_x = M2_expr_x.subs({C3v:c3v_sol, C4m:c4m_sol})

    # Convert M2_expr_x back to function of z => M2_expr(z):
    V2_expr = V2_expr_x.subs(x, z - H)
    M2_expr = M2_expr_x.subs(x, z - H)

    # ----------------------------------------------------------------
    # Now Slope/Deflection
    # We'll do the "moment-area" approach for each segment separately.
    # slope1(z)= ∫ [M1(z)/(E*Ix)] dz + constant, etc.
    # But we also want deflection continuity at z=H (plus zero at tip).
    # This can get quite large in symbolic form. We'll show the method.
    # ----------------------------------------------------------------

    EI = E*Ix

    # Segment1 slope/defl => 2 integration constants, say A1slope, A1defl
    A1slope, A1defl = sp.symbols('A1slope A1defl', real=True)
    slope1_indef = sp.integrate(M1_expr/EI, (z,))
    slope1_expr = slope1_indef + A1slope
    defl1_indef  = sp.integrate(slope1_expr, (z,))
    defl1_expr   = defl1_indef + A1defl

    # Segment2 slope/defl => 2 integration constants, say A2slope, A2defl
    A2slope, A2defl = sp.symbols('A2slope A2defl', real=True)
    slope2_indef = sp.integrate(M2_expr/EI, (z,))
    slope2_expr = slope2_indef + A2slope
    defl2_indef = sp.integrate(slope2_expr, (z,))
    defl2_expr  = defl2_indef + A2defl

    # We have 4 new unknowns: A1slope, A1defl, A2slope, A2defl
    # We want 4 boundary conditions for deflection:
    #   (i) continuity at z=H => defl1_expr(H)= defl2_expr(H)
    #   (ii) continuity of slope => slope1_expr(H)= slope2_expr(H)
    #   (iii) at z=H+D => defl2(H+D)=0
    #   (iv) at z=H+D => slope2(H+D)=0
    eq_defl = [
        sp.Eq(defl1_expr.subs(z,H), defl2_expr.subs(z,H)),
        sp.Eq(slope1_expr.subs(z,H), slope2_expr.subs(z,H)),
        sp.Eq(defl2_expr.subs(z,H+D), 0),
        sp.Eq(slope2_expr.subs(z,H+D), 0)
    ]

    sol_defl = sp.solve(eq_defl, (A1slope, A1defl, A2slope, A2defl), dict=True)
    if not sol_defl:
        raise ValueError("No solution for deflection boundary conditions.")
    sA1slope = sol_defl[0][A1slope]
    sA1defl  = sol_defl[0][A1defl]
    sA2slope = sol_defl[0][A2slope]
    sA2defl  = sol_defl[0][A2defl]

    # Substitute back:
    slope1_expr = slope1_expr.subs({A1slope:sA1slope, A1defl:sA1defl,
                                    A2slope:sA2slope, A2defl:sA2defl})
    defl1_expr  = defl1_expr.subs({A1slope:sA1slope, A1defl:sA1defl,
                                   A2slope:sA2slope, A2defl:sA2defl})
    slope2_expr = slope2_expr.subs({A1slope:sA1slope, A1defl:sA1defl,
                                    A2slope:sA2slope, A2defl:sA2defl})
    defl2_expr  = defl2_expr.subs({A1slope:sA1slope, A1defl:sA1defl,
                                   A2slope:sA2slope, A2defl:sA2defl})

    # ----------------------------------------------------------------
    # Evaluate arrays
    # ----------------------------------------------------------------
    def safe_eval(expr, zz):
        return float(expr.subs(z, zz))

    N = 200
    z_vals = np.linspace(0, total_depth, N)
    V_vals = []
    M_vals = []
    defl_vals = []

    for zz in z_vals:
        if zz <= H:
            Vz = safe_eval(V1_expr, zz)
            Mz = safe_eval(M1_expr, zz)
            wz = safe_eval(defl1_expr, zz)
        else:
            Vz = safe_eval(V2_expr, zz)
            Mz = safe_eval(M2_expr, zz)
            wz = safe_eval(defl2_expr, zz)
        V_vals.append(Vz)
        M_vals.append(Mz)
        defl_vals.append(wz)

    V_vals = np.array(V_vals)
    M_vals = np.array(M_vals)
    defl_vals = np.array(defl_vals)

    # max shear, moment, deflection
    max_shear = max(abs(V_vals))/1000.0
    max_moment = max(abs(M_vals))/1000.0
    max_deflection = max(abs(defl_vals))

    # quick stress checks
    fv = max_shear / A
    fv_allow = 0.44 * Fy
    fb = (max_moment*12) / Sx
    fb_allow = 0.66 * Fy
    shear_check = "OK" if fv<=fv_allow else "NG"
    moment_check = "OK" if fb<=fb_allow else "NG"

    # for plotting loads
    # use the same piecewise approach
    qA_arr = []
    qP_arr = []
    qS_arr = []
    for zz in z_vals:
        if zz<=H:
            # segment1 => active + surcharge
            qa = EFPa*spacing*zz
            qs = surcharge*spacing
            qA_arr.append(-qa - qs)
            qP_arr.append(0)
            qS_arr.append(-qs)
        else:
            # segment2 => active + passive
            qa = EFPa*spacing*zz
            qp = EFPp*spacing*(zz-H)
            qA_arr.append(-qa)
            qP_arr.append(qp)
            qS_arr.append(0)
    qA_arr = np.array(qA_arr)
    qP_arr = np.array(qP_arr)
    qS_arr = np.array(qS_arr)

    return {
        "z_vals": z_vals,
        "shear_vals": V_vals,
        "moment_vals": M_vals,
        "deflection_vals": defl_vals,
        "q_active": qA_arr,
        "q_passive": qP_arr,
        "q_surcharge": qS_arr,
        "max_shear": max_shear,
        "max_moment": max_moment,
        "max_deflection": max_deflection,
        "shear_stress": fv,
        "shear_allow": fv_allow,
        "shear_check": shear_check,
        "bending_stress": fb,
        "bending_allow": fb_allow,
        "moment_check": moment_check
    }

# -------------------------------------------------------------------
# 3) PLOT FUNCTION
# -------------------------------------------------------------------
def plot_shoring_diagrams(z_vals,
                          q_active=None, q_passive=None, q_surcharge=None,
                          shear_vals=None, moment_vals=None, deflection_vals=None):
    """
    Plot 4 diagrams: Load, Shear, Moment, Deflection
    """
    load_fig = go.Figure()
    if q_active is not None:
        load_fig.add_trace(go.Scatter(
            x=q_active, y=z_vals,
            fill='tozerox',
            name='Active',
            line=dict(color='red'),
            orientation='h'
        ))
    if q_passive is not None:
        load_fig.add_trace(go.Scatter(
            x=q_passive, y=z_vals,
            fill='tozerox',
            name='Passive',
            line=dict(color='orange'),
            orientation='h'
        ))
    if q_surcharge is not None:
        load_fig.add_trace(go.Scatter(
            x=q_surcharge, y=z_vals,
            fill='tozerox',
            name='Surcharge',
            line=dict(color='pink'),
            orientation='h'
        ))
    load_fig.update_yaxes(autorange='reversed')
    load_fig.update_layout(title="Load Diagram",
                           xaxis_title="q (psf)",
                           yaxis_title="Depth z (ft)")

    shear_fig = go.Figure()
    if shear_vals is not None:
        shear_fig.add_trace(go.Scatter(
            x=shear_vals, y=z_vals,
            fill='tozerox',
            name='Shear',
            line=dict(color='blue'),
            orientation='h'
        ))
    shear_fig.update_yaxes(autorange='reversed')
    shear_fig.update_layout(title="Shear Diagram",
                            xaxis_title="V (lb or kips)",
                            yaxis_title="Depth z (ft)")

    moment_fig = go.Figure()
    if moment_vals is not None:
        moment_fig.add_trace(go.Scatter(
            x=moment_vals, y=z_vals,
            fill='tozerox',
            name='Moment',
            line=dict(color='green'),
            orientation='h'
        ))
    moment_fig.update_yaxes(autorange='reversed')
    moment_fig.update_layout(title="Moment Diagram",
                             xaxis_title="M (ft-lb or kips-ft)",
                             yaxis_title="Depth z (ft)")

    deflection_fig = go.Figure()
    if deflection_vals is not None:
        deflection_fig.add_trace(go.Scatter(
            x=deflection_vals, y=z_vals,
            fill='tozerox',
            name='Deflection',
            line=dict(color='purple'),
            orientation='h'
        ))
    deflection_fig.update_yaxes(autorange='reversed')
    deflection_fig.update_layout(title="Deflection Diagram",
                                 xaxis_title="Deflection (in)",
                                 yaxis_title="Depth z (ft)")

    return load_fig, shear_fig, moment_fig, deflection_fig

# -------------------------------------------------------------------
# EXAMPLE USAGE
# -------------------------------------------------------------------
if __name__=="__main__":
    # H = 13.5
    # EFPa = 35.0
    # EFPp = 250.0
    # FS   = 1.3
    # spacing = 8.5
    # fy = 50.0
    # Ix = 3000.0
    # A  = 30.3
    # Sx = 245.0
    # E  = 29000.0
    # surcharge = 0

    H = 13.5
    EFPa = 35.0
    EFPp = 250.0
    FS   = 1.3
    spacing = 8.5
    fy = 50.0
    Ix = 1830.0
    A  = 20.1
    Sx = 154.0
    E  = 29000.0
    surcharge = 0

    # H = 16.5
    # EFPa = 35.0
    # EFPp = 250.0
    # FS   = 1.3
    # spacing = 8
    # fy = 50.0
    # Ix = 2850.0
    # A  = 24.7
    # Sx = 213.0
    # E  = 29000.0
    # surcharge = 0

    print("=== Two-Segment Cantilever Soldier Pile Example ===")
    D_req = cantilever_pile_design(H, EFPa, EFPp, surcharge, FS, spacing, fy)
    D0 = cantilever_pile_design(H, EFPa, EFPp, surcharge, 1, spacing, fy)
    print(f"Required Embedment Depth 0 = {D0:.2f} ft")
    print(f"Required Embedment Depth = {D_req:.2f} ft")
    print(f"Final Embedment Depth = {1.2 * D_req:.2f} ft")

    results = cantilever_pile_analysis_two_segment(
        H, D0, EFPa, EFPp,
        surcharge=surcharge, spacing=spacing,
        Ix=Ix, E=E, Sx=Sx, A=A, Fy=fy
    )


    results2 = cantilever_pile_analysis_two_segment(
        H, 0.25 * D0, EFPa, EFPp,
        surcharge=surcharge, spacing=spacing,
        Ix=Ix, E=E, Sx=Sx, A=A, Fy=fy
    )

    print("\n=== Analysis Results ===")
    print(f"Max Shear      = {results['max_shear']:.2f} kips")
    print(f"Max Moment     = {results['max_moment']:.2f} kips-ft")
    print(f"Max Deflection = {results2['max_deflection']:.3f} in")
    print(f"Shear Stress   = {results['shear_stress']:.2f} <= {results['shear_allow']:.2f}? {results['shear_check']}")
    print(f"Bending Stress = {results['bending_stress']:.2f} <= {results['bending_allow']:.2f}? {results['moment_check']}")

    # Plot diagrams
    figs = plot_shoring_diagrams(
        z_vals=results["z_vals"],
        q_active=results["q_active"],
        q_passive=results["q_passive"],
        q_surcharge=results["q_surcharge"],
        shear_vals=results["shear_vals"],
        moment_vals=results["moment_vals"],
        deflection_vals=results2["deflection_vals"]
    )
    load_fig, shear_fig, moment_fig, deflection_fig = figs
    import plotly.io as pio
    pio.renderers.default = 'browser'
    load_fig.show()
    shear_fig.show()
    moment_fig.show()
    deflection_fig.show()
