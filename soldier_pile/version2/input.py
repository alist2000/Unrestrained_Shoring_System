from cantilever_old import cantilever_pile_design, cantilever_pile_analysis


def handle_input(data):
    try:
        # -----------------------------
        # 2) EXTRACT INPUT PARAMETERS
        # -----------------------------
        # (a) General Properties
        FS = float(data["general_properties"]["FS"])  # Factor of Safety
        E_mod = float(data["general_properties"]["E"])  # Modulus of elasticity (ksi)
        pile_spacing = float(data["general_properties"]["Pile Spacing"])
        Fy = float(data["general_properties"]["Fy"])
        allow_deflection = float(
            data["general_properties"]["Allowable Deflection"])  # not used in design, but we store it

        # (b) Section Properties
        section_name = data["selected_section"]
        Ix = data["section_properties"]["Ix"]
        Sx = data["section_properties"]["Sx"]
        A = data["section_properties"]["A"]

        # (c) Soil Layers
        # For this example, we assume just one layer for user-defined approach:
        layer = data["soil_profile"]["layers"][0]
        H = layer["height"]  # Retaining height

        EFPa = layer["properties"]["EFP Active"]  # Active pressure coefficient
        EFPp = layer["properties"]["EFP Passive"]  # Passive pressure coefficient

        # (d) Surcharge
        # The "loads" array is empty, so we have no uniform load => 0
        # If you had a uniform load, you'd parse it here.
        surcharge_value = 0.0
        handle_surcharge(data["surcharge"])

        # -----------------------------
        # 3) CALL THE DESIGN FUNCTION
        # -----------------------------
        try:
            D_req = cantilever_pile_design(
                H=H,
                EFPa=EFPa,
                EFPp=EFPp,
                surcharge=surcharge_value,
                FS=FS,
                spacing=pile_spacing,
                fy=Fy,
                unit_system='us'
            )
        except ValueError as err:
            print(f"Error in design: {err}")
            D_req = None

        # -----------------------------
        # 4) CALL THE ANALYSIS FUNCTION
        #    (if D_req was found)
        # -----------------------------
        if D_req is not None:
            results = cantilever_pile_analysis(
                H=H,
                D=D_req,
                EFPa=EFPa,
                EFPp=EFPp,
                surcharge=surcharge_value,
                spacing=pile_spacing,
                Ix=Ix,
                E=E_mod,
                Sx=Sx,
                A=A,
                Fy=Fy
            )
        else:
            results = {}

        # -----------------------------
        # 5) PRINT ALL INPUT AND OUTPUT
        # -----------------------------
        print("\n=== INPUT PARAMETERS ===")
        print(f"General Info: {data['general_info']}")
        print(f"General Properties: FS={FS}, E={E_mod} ksi, Pile Spacing={pile_spacing} ft, Fy={Fy} ksi, "
              f"Allowable Deflection={allow_deflection} in")
        print(f"Selected Section: {section_name}")
        print(f"Section Properties: Ix={Ix} in^4, Sx={Sx} in^3, A={A} in^2")
        print(f"Soil Layer: H={H} ft, EFPa={EFPa}, EFPp={EFPp}")
        print(f"Surcharge: {surcharge_value} psf (uniform)")

        print("\n=== DESIGN & ANALYSIS RESULTS ===")
        if D_req is not None:
            print(f"Required Embedment (D) = {D_req:.2f} ft")
        else:
            print("D_req not found (design failed).")

        if results:
            print(f"Max Shear: {results['max_shear']} kips")
            print(f"Max Moment: {results['max_moment']} kip-ft")
            print(f"Max Deflection: {results['max_deflection']} in")
            print(f"Shear Status: {results['shear_status']}")
            print(f"Moment Status: {results['moment_status']}")
        else:
            print("No analysis results available (design may have failed).")
    except:
        print("Something went wrong.")


def handle_surcharge(surcharges):
    pass
