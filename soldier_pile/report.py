import pandas as pd
import pyarrow.feather as feather


# creating excel
def create_feather(z, value, title, excel_name):
    value = list(map(round_4, value))
    data = list(zip(z, value))
    df = pd.DataFrame(data, columns=["Z", title])
    df.to_feather("reports/excel/" + excel_name + ".feather")


def round_4(i):
    return round(i, 4)
