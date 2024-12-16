import frappe
from frappe.utils import flt, now

def execute(filters=None):
    """
    Execute function to generate salary report data.

    Args:
        filters (dict): Filters to apply to the report.

    Returns:
        list, list: Columns and data for the report.
    """
    columns = get_columns()
    data = []
    global employee_id
    
    if filters:
        employee_id = filters.get("employee")
        year = filters.get("year")
        if employee_id and year:
            data = get_report_data(employee_id, year)
    
    return columns, data

def get_columns():
    """
    Define columns for the salary report.

    Returns:
        list: Columns for the report.
    """
    return [
        {"fieldname": "month", "label": "Month", "fieldtype": "Data", "width": 100},
        {"fieldname": "basic_salary", "label": "Basic Salary", "fieldtype": "Currency", "width": 120},
        {"fieldname": "benefits_non_cash", "label": "Benefits Non-Cash", "fieldtype": "Currency", "width": 150},
        {"fieldname": "value_of_quarters", "label": "Value of Quarters", "fieldtype": "Currency", "width": 150},
        {"fieldname": "total_gross_pay", "label": "Total Gross Pay", "fieldtype": "Currency", "width": 120},
        {"fieldname": "defined_contribution_scheme", "label": "Defined Contribution Scheme", "fieldtype": "Currency", "width": 200},
        {"fieldname": "retirement_contribution_scheme", "label": "Retirement Contribution Scheme", "fieldtype": "Currency", "width": 220},
        {"fieldname": "owner_occupied_interest", "label": "Owner Occupied Interest", "fieldtype": "Currency", "width": 200},
        {"fieldname": "retirement_contribution_and_interest", "label": "Retirement Contribution & Owner Occupied Interest", "fieldtype": "Currency", "width": 300},
        {"fieldname": "chargeable_pay", "label": "Chargeable Pay", "fieldtype": "Currency", "width": 150},
        {"fieldname": "tax_charged", "label": "Tax Charged", "fieldtype": "Currency", "width": 120},
        {"fieldname": "personal_relief", "label": "Personal Relief", "fieldtype": "Currency", "width": 120},
        {"fieldname": "insurance_relief", "label": "Insurance Relief", "fieldtype": "Currency", "width": 120},
        {"fieldname": "paye_tax", "label": "PAYE Tax (J-K)", "fieldtype": "Currency", "width": 120}
    ]

def get_report_data(employee_id, year):
    """
    Retrieve salary report data for the specified employee and year.

    Args:
        employee_id (str): ID of the employee.
        year (str): Year for which the report is generated.

    Returns:
        list: Salary report data.
    """
    employee_details = frappe.get_doc("Employee", employee_id)
    company_details = frappe.get_doc("Company", employee_details.company)

    totals = {
        "basic_salary": 0,
        "benefits_non_cash": 0,
        "value_of_quarters": 0,
        "total_gross_pay": 0,
        "defined_contribution_scheme": 0,
        "retirement_contribution_scheme": 0,
        "owner_occupied_interest": 0,
        "retirement_contribution_and_interest": 0,
        "chargeable_pay": 0,
        "tax_charged": 0,
        "personal_relief": 0,
        "insurance_relief": 0,
        "paye_tax": 0
    }

    salary_slips = frappe.get_all(
        "Salary Slip",
        filters={
            "employee": employee_id,
            "start_date": [">=", f"{year}-01-01"],
            "end_date": ["<=", f"{year}-12-31"]
        },
        fields=["*"]
    )

    grouped_salary_slips = {}
    for slip in salary_slips:
        month = slip.end_date.strftime('%B')
        if month not in grouped_salary_slips:
            grouped_salary_slips[month] = []
        grouped_salary_slips[month].append(slip)

    monthly_data = []
    for month in [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]:
        if month in grouped_salary_slips:
            month_data = calculate_monthly_data(grouped_salary_slips[month])
            monthly_data.append({"month": month, **month_data})
            for key in totals:
                totals[key] += month_data.get(key, 0)
        else:
            monthly_data.append({
                "month": month,
                "basic_salary": 0.00,
                "benefits_non_cash": 0.00,
                "value_of_quarters": 0.00,
                "total_gross_pay": 0.00,
                "defined_contribution_scheme": 0.00,
                "retirement_contribution_scheme": 0.00,
                "owner_occupied_interest": 0.00,
                "retirement_contribution_and_interest": 0.00,
                "chargeable_pay": 0.00,
                "tax_charged": 0.00,
                "personal_relief": 0.00,
                "insurance_relief": 0.00,
                "paye_tax": 0.00
            })

    monthly_data.append({
        "month": "Total",
        **totals
    })

    return monthly_data

def calculate_monthly_data(salary_slips):
    """
    Calculate monthly salary data from salary slips.

    Args:
        salary_slips (list): List of salary slips for the month.

    Returns:
        dict: Monthly salary data.
    """
    monthly_totals = {
        "basic_salary": 0,
        "benefits_non_cash": 0,
        "value_of_quarters": 0,
        "total_gross_pay": 0,
        "defined_contribution_scheme": 0,
        "retirement_contribution_scheme": 0,
        "owner_occupied_interest": 0,
        "retirement_contribution_and_interest": 0,
        "chargeable_pay": 0,
        "tax_charged": 0,
        "personal_relief": 0,
        "insurance_relief": 0,
        "paye_tax": 0
    }

    for slip in salary_slips:
        
        # basic_salary = flt(frappe.db.get_value("Salary Detail", {'parent': slip.name, 'salary_component': 'Basic'}, 'amount'), 0)
        benefits_non_cash = get_benefits(slip.name) or 0.0
        basic_salary = get_basic(slip.name) or 0.00

        # if slip.earning_type == "Benefit":
        #     # Calculate non-cash benefits total from Salary Slip doctype
        #     benefits_non_cash = frappe.db.sql("""SELECT SUM(sd.amount) 
        #                                     FROM `tabSalary Slip` ss 
        #                                     INNER JOIN `tabSalary Detail` sd ON ss.name = sd.parent 
        #                                     INNER JOIN `tabSalary Component` sc ON sc.name = sd.salary_component 
        #                                     WHERE ss.name = '{}' 
        #                                     AND ss.employee = '{}' 
        #                                     AND sc.earning_type = 'Benefit'""".format(slip.name, employee_id))[0][0] or 0

        # elif slip.type == "Earning" and slip.earning_type == "Basic":
        #     # Calculate basic salary total from Salary Slip doctype
        #     basic_salary = frappe.db.sql("""SELECT SUM(sd.amount) 
        #                                 FROM `tabSalary Slip` ss 
        #                                 INNER JOIN `tabSalary Detail` sd ON ss.name = sd.parent 
        #                                 INNER JOIN `tabSalary Component` sc ON sc.name = sd.salary_component 
        #                                 WHERE ss.name = '{}' 
        #                                 AND ss.employee = '{}' 
        #                                 AND sc.earning_type = 'Basic'""".format(slip.name, employee_id))[0][0] or 0

        # Separate calculations for basic salary and non-cash benefits
        monthly_totals["basic_salary"] += basic_salary
        monthly_totals["benefits_non_cash"] += benefits_non_cash

        # Additional calculations for other components
        value_of_quarters = flt(frappe.db.get_value("Salary Detail", {'parent': slip.name, 'salary_component': 'Value of Quarters'}, 'amount'), 0)
        gross_pay = flt(slip.gross_pay, 0)
        retirement_contribution_scheme = get_actual_contribution(slip.name)
        chargeable_pay = flt(frappe.db.get_value("Salary Detail", {'parent': slip.name, 'salary_component': 'Taxable Income'}, 'amount'), 0)
        tax_charged = flt(frappe.db.get_value("Salary Detail", {'parent': slip.name, 'salary_component': 'Tax Charged'}, 'amount'), 0)
        personal_relief = flt(frappe.db.get_value("Salary Detail", {'parent': slip.name, 'salary_component': 'Personal Relief'}, 'amount'), 0)
        insurance_relief = flt(frappe.db.get_value("Salary Detail", {'parent': slip.name, 'salary_component': 'Insurance Relief'}, 'amount'), 0)
        paye_tax = flt(frappe.db.get_value("Salary Detail", {'parent': slip.name, 'salary_component': 'PAYE'}, 'amount'), 0)
        
        defined_contribution_scheme = get_actual_contribution(slip.name) + (basic_salary * 0.3)

        monthly_totals["value_of_quarters"] += value_of_quarters
        monthly_totals["total_gross_pay"] += gross_pay
        monthly_totals["defined_contribution_scheme"] += defined_contribution_scheme
        monthly_totals["retirement_contribution_scheme"] += retirement_contribution_scheme
        monthly_totals["chargeable_pay"] += chargeable_pay
        monthly_totals["tax_charged"] += tax_charged
        monthly_totals["personal_relief"] += personal_relief
        monthly_totals["insurance_relief"] += insurance_relief
        monthly_totals["owner_occupied_interest"] = get_actual_contribution(slip.name) or 0
        monthly_totals["paye_tax"] += paye_tax

    return monthly_totals



def get_actual_contribution(slip_name):
    """
    Calculate the actual retirement contribution for a given salary slip.

    Args:
        slip_name (str): Name of the salary slip.

    Returns:
        float: Actual contribution amount.
    """
    salary_details = frappe.get_all("Salary Detail", filters={'parent': slip_name}, fields=['salary_component', 'amount'])
    actual_contribution = [detail for detail in salary_details if detail['salary_component'] in ('NSSF Tier 1', 'NSSF Tier 2', 'EMP Voluntary NSSF')]
    actual_total = sum(flt(detail['amount'], 0) for detail in actual_contribution)
    return actual_total


def get_basic(slip_name):
    # Execute SQL query to fetch the basic salary amount for the given salary slip
    sql_query = """
        SELECT SUM(sd.amount) AS basic_salary
        FROM `tabSalary Slip` ss
        INNER JOIN `tabSalary Detail` sd ON ss.name = sd.parent
        INNER JOIN `tabSalary Component` sc ON sd.salary_component = sc.name
        WHERE ss.name = %s AND sc.earning_type = 'Basic'
    """
    basic_salary = frappe.db.sql(sql_query, (slip_name,), as_dict=True)
    
    # Extract the basic salary amount from the query result
    actual_total = basic_salary[0].get('basic_salary') if basic_salary else 0
    
    return actual_total

def get_benefits(slip_name):
    # Execute SQL query to fetch the basic salary amount for the given salary slip
    sql_query = """
        SELECT SUM(sd.amount) AS basic_salary
        FROM `tabSalary Slip` ss
        INNER JOIN `tabSalary Detail` sd ON ss.name = sd.parent
        INNER JOIN `tabSalary Component` sc ON sd.salary_component = sc.name
        WHERE ss.name = %s AND sc.earning_type = 'Benefit'
    """
    benefit= frappe.db.sql(sql_query, (slip_name,), as_dict=True)
    
    # Extract the basic salary amount from the query result
    actual_total = benefit[0].get('basic_salary') if benefit else 0
    
    return actual_total