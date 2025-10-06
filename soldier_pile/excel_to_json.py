import pandas as pd
import json
import os

# Load the Excel data into a pandas DataFrame
excel_path = r'C:/Users/Ali/Dropbox/Shoring/Reeves/ShoringData-REEVES_app.xlsx'  # Path to your Excel file
df = pd.read_excel(excel_path, header=None)

# Adjust column indexes based on your requirement (if necessary)
df = df.iloc[1:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]  # Adjust based on the number of columns

# Rename columns to match the structure
df.columns = ['PILE NUMBER', 'SPACING', 'RETAINED HEIGHT', 'EFP Active', 'EFP Passive', 'q_uniform', 'q_line',
              'L1_line', "Surcharge Depth", "Section"]

# Directory to store the generated JSON files
output_dir = r'E:\Git\Shoring\Unrestrained_Shoring_System\soldier_pile\save\Reeves\10062025'
os.makedirs(output_dir, exist_ok=True)

# Loop over each row and create a JSON file
for index, row in df.iterrows():
    # Extract pile data
    pile_number = row['PILE NUMBER']
    pile_spacing = row['SPACING']
    retaining_height = row['RETAINED HEIGHT']
    efp_active = row['EFP Active']  # Extract EFP Active
    efp_passive = row['EFP Passive']  # Extract EFP Passive
    q_uniform = row['q_uniform']  # Uniform load q
    q_line = row['q_line']  # Line load q
    L1_line = row['L1_line']  # Line load length
    surcharge_depth = row['Surcharge Depth']  # Line load length
    section = row['Section']  # Line load length

    # Determine load type and surcharge values
    if pd.notna(q_uniform) and q_uniform != 0:
        load_type = "Uniform"
        surcharge_q = q_uniform
        surcharge_L1 = None
    elif pd.notna(q_line) and q_line != 0:
        load_type = "Line Load"
        surcharge_q = q_line
        surcharge_L1 = L1_line
    else:
        load_type = "No Load"
        surcharge_q = None
        surcharge_L1 = None

    # Create a new JSON structure
    json_data = {
        "information": {
            "title": "1462 AND 1468 S. REEVES ST",
            "jobNo": "1462 AND 1468 S. REEVES ST",
            "designer": "AMIA ENGINEERING",
            "checker": "-",
            "company": "AMIA ENGINEERING",
            "client": "",
            "unit": "us",
            "date": None,
            "comment": f"#Pile {pile_number}",  # Update comment
            "other": None
        },
        "product_id": 26,
        "user_id": 44,
        "data": {
            "General data": {
                "FS": {"value": "1.3", "unit": None},
                "Fy": {"value": "50", "unit": "ksi"},
                "E": {"value": "29000", "unit": "ksi"},
                "Pile Spacing": {"value": str(round(float(pile_spacing), 2)), "unit": "ft"},  # Update pile spacing
                "Allowable Deflection": {"value": "10", "unit": "in"},
                # "Sections": {
                #     "value": "{\"id\":1380,\"item\":\"W21\",\"section_product_item\":\"39_91\"}",
                #     "unit": None
                # }
                # In your json_data dictionary, find the "Sections" key and modify it:

                "Sections": {
                    "value": f'{{"id":1380,"item":"{section}","section_product_item":"39_91"}}',  # <-- MODIFIED LINE
                    "unit": None
                }
            },
            "Soil Properties": {
                "Ka Surcharge": {"value": "1", "unit": None},
                "Equivalent Fluid Pressure Active": {"value": str(efp_active), "unit": "pcf"},  # Update EFP Active
                "Equivalent Fluid Pressure Passive": {"value": str(efp_passive), "unit": "pcf"},  # Update EFP Passive
                "Φ": {"value": "0", "unit": "°"},
                "γ": {"value": "20", "unit": "pcf"},
                "δ": {"value": "0", "unit": "°"},
                "β active": {"value": "0", "unit": "°"},
                "β passive": {"value": "0", "unit": "°"},
                "Formula": {
                    "value": "{\"id\":1439,\"item\":\"User Defined\",\"section_product_item\":\"41_94\"}",
                    "unit": None
                },
                "Retaining Height": {"value": str(round(float(retaining_height), 2)), "unit": "ft"}  # Update retaining height
            },
            "Surcharge": {
                "Load Type": {
                    "value": f"{{\"id\":1381,\"item\":\"{load_type}\",\"section_product_item\":\"48_92\"}}",
                    "unit": None
                },
                "Load Type ": {
                    "value": f"{{\"id\":1381,\"item\":\"{load_type}\",\"section_product_item\":\"48_92\"}}",
                    "unit": None
                },
                "Load Type  ": {
                    "value": f"{{\"id\":1381,\"item\":\"{load_type}\",\"section_product_item\":\"48_92\"}}",
                    "unit": None
                },
                "Load Type   ": {
                    "value": f"{{\"id\":1381,\"item\":\"{load_type}\",\"section_product_item\":\"48_92\"}}",
                    "unit": None
                },
                "q": {"value": str(surcharge_q), "unit": None},
                "q ": {"value": str(surcharge_q), "unit": None},
                "q  ": {"value": str(surcharge_q), "unit": None},
                "q   ": {"value": str(surcharge_q), "unit": None},
                "L1": {"value": str(surcharge_L1), "unit": "ft"} if surcharge_L1 else None,
                "L1 ": {"value": str(surcharge_L1), "unit": "ft"} if surcharge_L1 else None,
                "L1  ": {"value": str(surcharge_L1), "unit": "ft"} if surcharge_L1 else None,
                "L1   ": {"value": str(surcharge_L1), "unit": "ft"} if surcharge_L1 else None,
                "Surcharge Effective Depth": {"value": str(round(float(surcharge_depth), 2)), "unit": "ft"}
            },
            "Lagging": {
                "Ph max": {"value": "400", "unit": "psf"},
                "Fb": {"value": "0.9", "unit": "ksi"},
                "Timber Size": {
                    "value": "{\"id\":1403,\"item\":\"4 x 12\",\"section_product_item\":\"42_93\"}",
                    "unit": None
                }
            }
        },
        "type": 1,
        "number_of_projects": 1
    }

    # Define the output file path for this pile
    output_file_path = os.path.join(output_dir, f"pile_{pile_number}.json")

    # Write the JSON data to the file
    with open(output_file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

print("JSON files have been created successfully!")
