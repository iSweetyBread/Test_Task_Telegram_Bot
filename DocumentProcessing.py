from xhtml2pdf import pisa
from jinja2 import Template
from datetime import datetime
import random

# Helper function, that converts html content into pdf document
def convert_html_to_pdf(source_html, output_filename):
    # Opens the output file in binary write mode and uses xhtml2pdf (pisa) to create a PDF
    with open(output_filename, "wb") as result_file:
        pisa_status = pisa.CreatePDF(source_html, dest=result_file)
    # Returns 0 if successful, or error code otherwise
    return pisa_status.err

# Helper function, that processes user's data and creates a document based in a template
def process_doc(data_input):
    # Opens and reads the html template
    with open("InsuranceTemplate.html") as f:
        template = Template(f.read())

    # Default data structure with required data fields
    data = {
        "name": "",
        "surname": "",
        "date_of_birth": "",
        "address": "",
        "car_make": "",
        "car_model": "",
        "car_year": "",
        "car_registration": "",
        "policy_number": "",
        "start_date": "",
        "end_date": "",
        "premium_amount": "100 USD",
        "issue_date": ""
    }

    # Fills the data dictionary with values from input, preserving default if empty
    for key in data_input:
        current_value = data.get(key, '')
        new_value = data_input[key]
        data[key] = current_value if current_value else new_value

    # Gets today's date
    today = datetime.today()

    # Calculates the first day of the next month for "start_date" field
    year = today.year + (1 if today.month == 12 else 0)
    month = 1 if today.month == 12 else today.month + 1
    start_date = datetime(year, month, 1)

    # Calculates the date - 1 year in the future - for "end_date" field
    end_date = start_date.replace(year=start_date.year + 1)

    # Sets calculated dates, formating them into DD.MM.YYYY
    data["start_date"] = start_date.strftime("%d.%m.%Y")
    data["end_date"] = end_date.strftime("%d.%m.%Y")
    data["issue_date"] = today.strftime("%d.%m.%Y")

    # Generates random policy number
    data["policy_number"] = str(random.randint(10**15, 10**16 - 1))

    # Renders the html with the filled-in data
    rendered_doc = template.render(data)
    # Converts the html into a pdf
    convert_html_to_pdf(rendered_doc, 'FinalDocument.pdf')