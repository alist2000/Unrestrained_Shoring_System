import sqlite3
import pathlib

# --- Define Base Paths ---
# This ensures that paths are resolved correctly regardless of where this script is imported from.
# The path is constructed relative to the location of this file (database.py).
try:
    # Get the directory containing this script.
    # e.g., .../Shoring/Unrestrained_Shoring_System/
    SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

    # The project root is one level up from this script's directory.
    # e.g., .../Shoring/
    PROJECT_ROOT1 = SCRIPT_DIR.parent
    PROJECT_ROOT = PROJECT_ROOT1.parent
    # The database folder is in the project root.
    DB_FOLDER_PATH = PROJECT_ROOT / "database"
except NameError:
    # Fallback for environments where __file__ is not defined (e.g., some interactive interpreters).
    # This assumes the script is run from a directory where './database' is a valid relative path.
    DB_FOLDER_PATH = pathlib.Path("database")

# --- Create and Initialize Databases ---
# The following blocks now use the dynamically constructed DB_FOLDER_PATH.

# US Database
dbase_us_path = DB_FOLDER_PATH / "stahl_us.db"
sql_us_path = DB_FOLDER_PATH / "Stahl_Soldier_pile_us.sql"
print("sql_us_path = ", dbase_us_path)

try:
    dbase = sqlite3.connect(dbase_us_path)
    cursor = dbase.cursor()
    with open(sql_us_path) as stahl_file:
        stahl_r = stahl_file.read()
    cursor.executescript(stahl_r)
    dbase.close()
except sqlite3.Error as e:
    print(f"Database error with US Stahl DB: {e}")
    pass
except FileNotFoundError:
    print(f"SQL file not found at: {sql_us_path}")
    pass

# Metric Database
try:
    dbase_metric_path = DB_FOLDER_PATH / "stahl_metric.db"
    sql_metric_path = DB_FOLDER_PATH / "Stahl_Soldier_pile_metric.sql"
    dbase = sqlite3.connect(dbase_metric_path)
    cursor = dbase.cursor()
    with open(sql_metric_path) as stahl_file:
        stahl_r = stahl_file.read()
    cursor.executescript(stahl_r)
    dbase.close()
except sqlite3.Error as e:
    # print(f"Database error with Metric Stahl DB: {e}")
    pass
except FileNotFoundError:
    # print(f"SQL file not found at: {sql_metric_path}")
    pass

# Timber Database
try:
    dbase_timber_path = DB_FOLDER_PATH / "timber.db"
    sql_timber_path = DB_FOLDER_PATH / "timber_size.sql"
    dbase = sqlite3.connect(dbase_timber_path)
    cursor = dbase.cursor()
    with open(sql_timber_path) as timber_file:
        timber_r = timber_file.read()
    cursor.executescript(timber_r)
    dbase.close()
except sqlite3.Error as e:
    # print(f"Database error with Timber DB: {e}")
    pass
except FileNotFoundError:
    # print(f"SQL file not found at: {sql_timber_path}")
    pass


def SQL_reader(w, A_min, S_min, Ix_min, unit_system):
    """
    Reads steel section properties from the appropriate database.
    """
    w = str(w)
    dbase_path = DB_FOLDER_PATH / f'stahl_{unit_system}.db'

    try:
        dbase = sqlite3.connect(dbase_path)
        cursor = dbase.cursor()
        sql_select_Query = "SELECT EDI_Std_Nomenclature, Ix, ag, Sx, wc, d, bf, tw, tf FROM stahl WHERE title = ?"
        cursor.execute(sql_select_Query, [w])
        parameters = cursor.fetchall()
        dbase.close()
    except sqlite3.Error:
        return {}  # Return empty on DB error

    solution = []
    for item in parameters:
        # Ensure values are valid floats before comparison
        try:
            if float(item[1]) >= Ix_min and float(item[2]) >= A_min and float(item[3]) >= S_min:
                solution.append(item)
        except (ValueError, TypeError):
            continue

    if not solution:
        return {}  # Return empty if no sections meet criteria

    # Choose the section with the minimum weight
    final = min(solution, key=lambda x: float(x[4]))

    return {
        "section": final[0], "Ix": float(final[1]), "area": float(final[2]),
        "Sx": float(final[3]), "wc": float(final[4]), "h": float(final[5]),
        "bf": float(final[6]), "tw": float(final[7]), "tf": float(final[8])
    }


def SQL_reader_timber(section, unit_system):
    """
    Reads timber dimensions from the database.
    """
    dbase_path = DB_FOLDER_PATH / 'timber.db'
    try:
        dbase = sqlite3.connect(dbase_path)
        cursor = dbase.cursor()
        sql_select_Query = "SELECT b_actual_size_inches, h_actual_size_inches, b_actual_size_mm, h_actual_size_mm FROM timber WHERE nominal_size = ?"
        cursor.execute(sql_select_Query, [section])
        parameters = cursor.fetchone()
        dbase.close()
    except sqlite3.Error:
        return {}  # Return empty on DB error

    if not parameters:
        return {}

    if unit_system == "us":
        b_val, h_val = parameters[0], parameters[1]
    else:
        b_val, h_val = parameters[2], parameters[3]

    return {"b": b_val, "h": h_val}