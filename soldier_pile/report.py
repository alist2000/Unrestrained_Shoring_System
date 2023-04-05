import pandas as pd
import pyarrow.feather as feather
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader


# creating excel
def create_feather(z, value, title, excel_name):
    value = list(map(lambda x: round(x, 4), value))
    data = list(zip(z, value))
    df = pd.DataFrame(data, columns=["Z", title])
    df.to_feather("reports/excel/" + excel_name + ".feather")


def choose_and_create_pdf_unrestrained(file_name):
    file = open("reports/template/" + file_name + ".html", "r")
    html_filled = file.read()
    # file_name is a name with .html suffix it must be replaced with .pdf
    pdf_name = file.name[:-5] + ".pdf"
    file.close()
    HTML(string=html_filled, base_url=__file__).write_pdf(pdf_name)

choose_and_create_pdf_unrestrained("Rep_Unrestrained")