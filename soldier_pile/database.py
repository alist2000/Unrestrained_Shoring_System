import sqlite3

# create database file
dbase = sqlite3.connect("../../database/stahl_us.db")
cursor = dbase.cursor()
stahl = open("../../database/Stahl_Soldier_pile_us.sql")
stahl_r = stahl.read()
try:
    cursor.executescript(stahl_r[3:])
    # print("Done!")
except:
    # print("fail!")
    pass

# create database file
dbase = sqlite3.connect("../../database/stahl_metric.db")
cursor = dbase.cursor()
stahl = open("../../database/Stahl_Soldier_pile_metric.sql")
stahl_r = stahl.read()
try:
    cursor.executescript(stahl_r[3:])
    # print("Done!")
except:
    # print("fail!")
    pass

# create database file
dbase = sqlite3.connect("../../database/timber.db")
cursor = dbase.cursor()
timber = open("../../database/timber_size.sql")
timber_r = timber.read()
try:
    cursor.executescript(timber_r)
    # print("Done!")
except:
    # print("fail!")
    pass


def SQL_reader(w, A_min, S_min, Ix_min, unit_system):
    w = str(w)
    # dbase = sqlite3.connect('/app/app/bfp/database/stahl.db')  # Open a database File in host
    dbase = sqlite3.connect('../../database/stahl_' + unit_system + '.db')  # Open a database File in local
    cursor = dbase.cursor()
    sql_select_Query = "SELECT EDI_Std_Nomenclature,Ix ,ag , Sx, wc, d, bf, tw, tf FROM stahl WHERE title = ?"
    cursor.execute(sql_select_Query, [w])
    parameters = cursor.fetchall()

    solution = []
    for item in parameters:
        if float(item[1]) >= Ix_min and float(item[2]) >= A_min and float(item[3]) >= S_min:
            solution.append(item)
    weight = 9999999999999999  # just a big number.
    # choose section with less weight
    for i in solution:
        if float(i[4]) <= weight:
            final = i
    try:
        section = final[0]
        Ix = float(final[1])
        area = float(final[2])
        Sx = float(final[3])
        wc = float(final[4])
        h = float(final[5])
        bf = float(final[6])
        tw = float(final[7])
        tf = float(final[8])
    except:
        section = ""
        Ix = ""
        area = ""
        Sx = ""
        wc = ""
        h = ""
        bf = ""
        tw = ""
        tf = ""
    dbase.close()
    return {"section": section, "Ix": Ix, "area": area, "Sx": Sx,"wc": wc, "h": h, "bf": bf, "tw": tw, "tf": tf}


def SQL_reader_timber(section, unit_system):
    dbase = sqlite3.connect('../../database/timber.db')  # Open a database File in local
    cursor = dbase.cursor()
    sql_select_Query = "SELECT b_actual_size_inches, h_actual_size_inches, b_actual_size_mm,h_actual_size_mm FROM timber WHERE nominal_size = ?"
    cursor.execute(sql_select_Query, [section])
    parameters = cursor.fetchone()
    if unit_system == "us":
        b = parameters[0]  # inches
        h = parameters[1]
    else:
        b = parameters[2]  # mm
        h = parameters[3]

    dbase.close()
    return {"b": b, "h": h}

# output = SQL_reader_timber("3 x 12", "us")
# output = SQL_reader('40', 150, 1900, 'us')
