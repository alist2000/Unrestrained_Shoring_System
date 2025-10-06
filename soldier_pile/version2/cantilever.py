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
    eq = sp.Eq(Mp, FS*(Ma + Msurch))
    sol = sp.solve(eq, D)
    D_sol = [s for s in sol if s.is_real and s>0]
    if not D_sol:
        raise ValueError("No positive real solution for D.")
    return float(min(D_sol))


# -------------------------------------------------------------------
# 2) TWO-SEGMENT ANALYSIS: (Shear, Moment, *and* Deflection)
# -------------------------------------------------------------------
def cantilever_pile_analysis_two_segment(H, D, EFPa, EFPp,
                                         surcharge=0, spacing=1.0,
                                         Ix=500, E=29000,
                                         Sx=154.0, A=20.1, Fy=50.0):
    """
    Two-segment approach:
      Segment 1: z in [0, H]   (above grade)
        -> Boundary conditions at top: V1(0)=0, M1(0)=0 (free)
      Segment 2: z in [H, H+D] (embedded)
        -> Continuity at z=H => M1(H)=M2(H), V1(H)=V2(H)
        -> At tip (z=H+D) => deflection=0, slope=0 (fully fixed)

    1) We first do shear & moment in each segment:
       V1'(z)=q1(z),  M1'(z)=V1(z)   [with BC: V1(0)=0, M1(0)=0]
       V2'(z)=q2(z),  M2'(z)=V2(z)   [with continuity at z=H]
    2) Then "moment-area" for deflection in each segment,
       imposing continuity at z=H (deflection & slope) plus
       deflection=0 & slope=0 at z=H+D.

    Returns dict with z-array, shear, moment, deflection, etc.
    """

    # Symbolic variable
    z = sp.Symbol('z', real=True, nonnegative=True)
    total_depth = H + D
    EI = E * Ix

    # ----------------------------------------------------------------
    # 2.1) Define piecewise lateral load
    # ----------------------------------------------------------------
    # Segment 1 (0..H): q1(z)
    #   Active = EFPa*z, Surcharge = surcharge, both negative to left
    q1 = -(EFPa*spacing*z + surcharge*spacing)

    # Segment 2 (H..H+D): q2(z)
    #   Active = EFPa*z, Passive = EFPp*(z-H)
    #   So net q2 = -[EFPa*z] + [EFPp*(z-H)] times spacing
    q2 = -(EFPa*spacing*z) + (EFPp*spacing*(z - H))

    # ----------------------------------------------------------------
    # 2.2) Solve Shear & Moment in Segment 1
    # ----------------------------------------------------------------
    C1v, C2m = sp.symbols('C1v C2m', real=True)

    # V1(z) = ∫(q1 dz) from 0..z + C1v
    V1_expr = sp.integrate(q1, (z,0,z)) + C1v

    # M1(z) = ∫(V1_expr dz) from 0..z + C2m
    M1_expr = sp.integrate(V1_expr, (z,0,z)) + C2m

    # BC at z=0 => V1(0)=0, M1(0)=0
    eq_s1 = [
        sp.Eq(V1_expr.subs(z,0), 0),
        sp.Eq(M1_expr.subs(z,0), 0)
    ]
    sol_s1 = sp.solve(eq_s1, (C1v, C2m), dict=True)
    c1v_sol = sol_s1[0][C1v]
    c2m_sol = sol_s1[0][C2m]

    # Substitute
    V1_expr = V1_expr.subs({C1v:c1v_sol, C2m:c2m_sol})
    M1_expr = M1_expr.subs({C1v:c1v_sol, C2m:c2m_sol})

    # ----------------------------------------------------------------
    # 2.3) Solve Shear & Moment in Segment 2
    # ----------------------------------------------------------------
    x = sp.Symbol('x', real=True, nonnegative=True)
    C3v, C4m = sp.symbols('C3v C4m', real=True)

    # shift z => x = z-H
    q2_x = q2.subs(z, H + x)

    V2_expr_x = sp.integrate(q2_x, (x,0,x)) + C3v
    M2_expr_x = sp.integrate(V2_expr_x, (x,0,x)) + C4m

    # continuity at x=0 => z=H => V2(0)=V1(H), M2(0)=M1(H)
    eq_s2 = [
        sp.Eq(V2_expr_x.subs(x,0), V1_expr.subs(z,H)),
        sp.Eq(M2_expr_x.subs(x,0), M1_expr.subs(z,H))
    ]
    sol_s2 = sp.solve(eq_s2, (C3v, C4m), dict=True)
    c3v_sol = sol_s2[0][C3v]
    c4m_sol = sol_s2[0][C4m]

    # final V2, M2 in terms of z
    V2_expr = V2_expr_x.subs({C3v:c3v_sol, C4m:c4m_sol}).subs(x, z - H)
    M2_expr = M2_expr_x.subs({C3v:c3v_sol, C4m:c4m_sol}).subs(x, z - H)

    # ----------------------------------------------------------------
    # 2.4) Deflection in Segment 1 (moment-area)
    # ----------------------------------------------------------------
    A1slope, A1defl = sp.symbols('A1slope A1defl', real=True)

    slope1_indef = sp.integrate(M1_expr/EI, (z,))
    slope1_expr  = slope1_indef + A1slope

    defl1_indef  = sp.integrate(slope1_expr, (z,))
    defl1_expr   = defl1_indef + A1defl

    # ----------------------------------------------------------------
    # 2.5) Deflection in Segment 2
    # ----------------------------------------------------------------
    A2slope, A2defl = sp.symbols('A2slope A2defl', real=True)

    slope2_indef = sp.integrate(M2_expr/EI, (z,))
    slope2_expr  = slope2_indef + A2slope

    defl2_indef  = sp.integrate(slope2_expr, (z,))
    defl2_expr   = defl2_indef + A2defl

    # boundary conditions for deflection:
    #   (1) continuity deflection at z=H => defl1(H)=defl2(H)
    #   (2) continuity slope at z=H => slope1(H)=slope2(H)
    #   (3) tip deflection = 0 => defl2(H+D)=0
    #   (4) tip slope = 0 => slope2(H+D)=0
    eq_defl = [
        sp.Eq(defl1_expr.subs(z,H), defl2_expr.subs(z,H)),
        sp.Eq(slope1_expr.subs(z,H), slope2_expr.subs(z,H)),
        sp.Eq(defl2_expr.subs(z,H+D), 0),
        sp.Eq(slope2_expr.subs(z,H+D), 0)
    ]
    sol_defl = sp.solve(eq_defl, (A1slope, A1defl, A2slope, A2defl), dict=True)
    sA1slope = sol_defl[0][A1slope]
    sA1defl  = sol_defl[0][A1defl]
    sA2slope = sol_defl[0][A2slope]
    sA2defl  = sol_defl[0][A2defl]

    # substitute
    slope1_expr = slope1_expr.subs(sol_defl[0])
    defl1_expr  = defl1_expr.subs(sol_defl[0])
    slope2_expr = slope2_expr.subs(sol_defl[0])
    defl2_expr  = defl2_expr.subs(sol_defl[0])

    # ----------------------------------------------------------------
    # 2.6) Evaluate on a z-array
    # ----------------------------------------------------------------
    def safe_eval(expr, val):
        return float(expr.subs(z, val))

    N = 200
    z_vals = np.linspace(0, total_depth, N)
    V_vals = []
    M_vals = []
    w_vals = []

    for zz in z_vals:
        if zz <= H:
            Vv = safe_eval(V1_expr, zz)
            Mv = safe_eval(M1_expr, zz)
            wv = safe_eval(defl1_expr, zz)
        else:
            Vv = safe_eval(V2_expr, zz)
            Mv = safe_eval(M2_expr, zz)
            wv = safe_eval(defl2_expr, zz)
        V_vals.append(Vv)
        M_vals.append(Mv)
        w_vals.append(wv)

    V_vals = np.array(V_vals)
    M_vals = np.array(M_vals)
    w_vals = np.array(w_vals)

    # max shear, moment, deflection
    max_shear = max(abs(V_vals))/1000.0
    max_moment= max(abs(M_vals))/1000.0
    max_defl  = max(abs(w_vals))

    # stress checks
    fv = max_shear / A
    fv_allow = 0.44 * Fy
    fb = (max_moment*12) / Sx
    fb_allow = 0.66 * Fy
    shear_check  = "OK" if fv<=fv_allow else "NG"
    moment_check = "OK" if fb<=fb_allow else "NG"

    # for load diagram
    qA_arr = []
    qP_arr = []
    qS_arr = []
    for zz in z_vals:
        if zz <= H:
            qa = EFPa*spacing*zz
            qs = surcharge*spacing
            qA_arr.append(-qa - qs)
            qP_arr.append(0)
            qS_arr.append(-qs)
        else:
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
        "deflection_vals": w_vals,
        "q_active": qA_arr,
        "q_passive": qP_arr,
        "q_surcharge": qS_arr,
        "max_shear": max_shear,
        "max_moment": max_moment,
        "max_deflection": max_defl,
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
                           xaxis_title="q (psf or lb/ft, depending on your usage)",
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
                             xaxis_title="M (ft-lb or kip-ft)",
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
                                 xaxis_title="Deflection (check units!)",
                                 yaxis_title="Depth z (ft)")

    return load_fig, shear_fig, moment_fig, deflection_fig


# -------------------------------------------------------------------
# EXAMPLE / TEST
# -------------------------------------------------------------------
if __name__=="__main__":
    # Example usage
    H = 13.5
    EFPa = 46.0
    EFPp = 250.0
    FS   = 1.3     # Try FS=1 or any number (1.3, 1.5, etc.)
    spacing = 8.0
    fy = 50.0
    Ix = 1330.0
    A  = 18.3
    Sx = 127.0
    E  = 29000.0
    surcharge = 0

    print("=== Two-Segment Cantilever Pile Example (with Deflection) ===")
    # 1) solve for embedment
    D_req = cantilever_pile_design(H, EFPa, EFPp, surcharge, FS, spacing, fy)
    print(f"Required Embedment (FS={FS}) = {D_req:.2f} ft")

    # 2) run two-segment analysis
    results = cantilever_pile_analysis_two_segment(
        H, D_req, EFPa, EFPp,
        surcharge=surcharge,
        spacing=spacing,
        Ix=Ix, E=E, Sx=Sx, A=A, Fy=fy
    )
    results2 = cantilever_pile_analysis_two_segment(
        H, 3, EFPa, EFPp,
        surcharge=surcharge,
        spacing=spacing,
        Ix=Ix, E=E, Sx=Sx, A=A, Fy=fy
    )
    print("\n=== RESULTS ===")
    print(f"Max Shear      = {results['max_shear']:.2f} kips")
    print(f"Max Moment     = {results['max_moment']:.2f} kips-ft")
    print(f"Max Deflection = {results2['max_deflection']:.4f} in")
    print(f"Shear Stress   = {results['shear_stress']:.2f} <= {results['shear_allow']:.2f}? {results['shear_check']}")
    print(f"Bending Stress = {results['bending_stress']:.2f} <= {results['bending_allow']:.2f}? {results['moment_check']}")

    # 3) Plot
    zvals   = results["z_vals"]
    qactive = results["q_active"]
    qpass   = results["q_passive"]
    qsurch  = results["q_surcharge"]
    shearv  = results["shear_vals"]
    momentv = results["moment_vals"]
    defl    = results["deflection_vals"]

    figs = plot_shoring_diagrams(
        zvals,
        q_active=qactive,
        q_passive=qpass,
        q_surcharge=qsurch,
        shear_vals=shearv,
        moment_vals=momentv,
        deflection_vals=defl
    )
    figs[0].show()
    figs[1].show()
    figs[2].show()
    figs[3].show()
