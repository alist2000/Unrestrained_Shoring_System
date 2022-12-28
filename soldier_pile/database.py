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


def SQL_reader(w, A_min, S_min, unit_system):
    # dbase = sqlite3.connect('/app/app/bfp/database/stahl.db')  # Open a database File in host
    dbase = sqlite3.connect('../../database/stahl_' + unit_system + '.db')  # Open a database File in local
    cursor = dbase.cursor()
    sql_select_Query = "SELECT EDI_Std_Nomenclature,Ix ,ag , Sx, wc FROM stahl WHERE title = ?"
    cursor.execute(sql_select_Query, [w])
    parameters = cursor.fetchall()
    solution = []
    for item in parameters:
        if float(item[2]) >= A_min and float(item[3]) >= S_min:
            solution.append(item)

    # # all section that is ok
    # section_list = []
    # Ix_list = []
    # weight_list = []
    # for i in solution:
    #     section = i[0]
    #     Ix = i[1]
    #     weight = i[4]
    #     section_list.append(section)
    #     Ix_list.append(Ix)
    #     weight_list.append(weight)
    weight = 9999999999999999 # just a big number.
    # choose section with less weight
    for i in solution:
        if float(i[4]) <= weight:
            final = i
    try:
        section = final[0]
        Ix = final[1]
    except:
        section = ""
        Ix = ""
    dbase.close()
    return {"section": section, "Ix": Ix}


output = SQL_reader('40', 150, 1900, 'us')
