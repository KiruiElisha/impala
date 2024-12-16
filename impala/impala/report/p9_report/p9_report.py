# Copyright (c) 2023, Aqiq and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr
import calendar
import datetime


def execute(filters=None):
    columns, data = get_columns(), []

    employee_vals = frappe.db.get_value(
        "Employee",
        {"name": filters.get("employee")},
        ["name", "employee_name", "employee_pin"],
        as_dict=True,
    )
    months_of_the_year = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]

    for month in months_of_the_year:
        conditions = ""
        if filters.get("company"):
            conditions += " and ss.company='{}'".format(filters.get("company"))
        if filters.get("employee"):
            conditions += " and ss.employee='{}'".format(filters.get("employee"))
        if month and filters.get("fiscal_year"):
            payroll_yr = filters.get("fiscal_year")
            datetime_object = datetime.datetime.strptime(month, "%B")
            month_number = datetime_object.month
            month_end = datetime.date(
                int(payroll_yr), month_number + 1 if month_number < 12 else 1, 1
            ) - datetime.timedelta(days=1)
            month_end = month_end.strftime("%Y-%m-%d")
            month_number = (
                "0" + str(month_number) if month_number < 9 else str(month_number)
            )
            month_start = str(payroll_yr) + "-" + month_number + "-" + "01"
            conditions += " and ss.end_date >='{}' AND ss.end_date<='{}'".format(
                month_start, month_end
            )

            row = {}
            row["month_name"] = month
            row["gross_salary"] = 0
            row["basic"] = 0
            row["benefits"] = 0
            row["value_of_quarters"] = 0
            row["gross_pay"] = 0
            row["def_contr_ret_scheme_e1"] = 0
            row["def_contr_ret_scheme_e2"] = 0
            row["def_contr_ret_scheme_e3"] = 0
            row["saving_amount_of_interest"] = 0
            row["owner_the_lowest_of_e_added"] = 0
            row["charge_pay"] = 0
            row["tax_charged"] = 0
            row["nssf_tier_1"] = 0
            row["nssf_tier_2"] = 0
            row["emp_voluntary_nssf"] = 0
            row["personal_relief"] = 0
            row["insurance_relief"] = 0
            row["total_relief"]=0
            row["paye"] = 0
            row["negative_paye"]=0
            
            salary_slips = frappe.db.get_list(
                "Salary Slip",
                {
                    "employee": filters.get("employee"),
                    "posting_date": ["between", [month_start, month_end]],
                },
                pluck="name",
                debug=False,
            )

            for slip in salary_slips:
                salary_slip_details = get_salary_details_for_employee(
                    filters, conditions, slip
                )
                if salary_slip_details:
                    for s in salary_slip_details:
                        if s.earning_type == "Benefit":
                            row["benefits"] += s.amount or 0.0
                        elif s.earning_type == "Basic":
                            row["gross_pay"] += s.amount or 0.0
                        if s.salary_component == "Basic":
                            row["basic"] = s.amount or 0
                        elif s.salary_component == "Gross Salary":
                            row["gross_salary"] = s.amount or 0
                        elif s.salary_component == "Value of Quarters":
                            row["value_of_quarters"] = s.amount
                        elif s.salary_component == "NSSF Tier 1":
                            row["nssf_tier_1"] = s.amount or 0
                        elif s.salary_component == "NSSF Tier 2":
                            row["nssf_tier_2"] = s.amount or 0
                        elif s.salary_component == "EMP Voluntary NSSF":
                            row["emp_voluntary_nssf"] = s.amount or 0
                        # elif s.salary_component == "NOT Defined":
                        #     row["def_contr_ret_scheme_e1"] = s.amount
                        elif s.salary_component == "NOT Defined":
                            row["def_contr_ret_scheme_e3"] = s.amount
                        elif s.salary_component == "NOT Defined":
                            row["saving_amount_of_interest"] = s.amount
                        elif s.salary_component == "NOT Defined":
                            row["owner_the_lowest_of_e_added"] = s.amount
                        elif s.salary_component == "Taxable Income":
                            row["charge_pay"] = s.amount
                        elif s.salary_component == "Tax Charged":
                            row["tax_charged"] = s.amount
                        elif s.salary_component == "Personal Relief":
                            row["personal_relief"] = s.amount
                        elif s.salary_component == "Insurance Relief":
                            row["insurance_relief"] = s.amount
                        elif s.salary_component == "PAYE":
                            row["paye"] = s.amount
                        elif s.salary_component =="Negative PAYE":
                            row["negative_paye"]=s.amount
            row["def_contr_ret_scheme_e1"]=0.3 * row["gross_salary"]

            row["def_contr_ret_scheme_e2"] = (
                row["nssf_tier_1"] +
                row["nssf_tier_2"] +
                row["emp_voluntary_nssf"]
            )
            row["total_relief"] = (
                row["personal_relief"] +
                row["insurance_relief"]
            )            
            data.append(row)

    return columns, data



def get_salary_details_for_employee(filters, conditions, slip):

    # -- return frappe.db.sql("""SELECT sd.salary_component, sd.amount FROM `tabSalary Slip` ss INNER JOIN `tabSalary Detail` sd on ss.name=sd.parent WHERE ss.name='%s' %s"""%(slip, conditions), as_dict=True, debug=True)
    return frappe.db.sql(
        """select sd.salary_component, sd.amount, 
		sc.earning_type
		FROM `tabSalary Slip` ss 
		INNER JOIN `tabSalary Detail` sd on ss.name=sd.parent 
		INNER JOIN `tabSalary Component` sc on sc.name=sd.salary_component 
		WHERE ss.name='%s' %s
		"""
        % (slip, conditions),
        as_dict=True,
        debug=True,
    )


def get_conditions(filters):
    # conditions = ""
    # if filters.get("company"):
    # 	conditions += " and ss.company='{}'".format(filters.get("company"))
    # if filters.get("employee"):
    # 	conditions += " and ss.employee='{}'".format(filters.get("employee"))

    # if filters.get("from_date"):
    # 	conditions += " and ss.posting_date>='{}'".format(filters.get("from_date"))
    # if filters.get("to_date"):
    # 	conditions += " and ss.posting_date<='{}'".format(filters.get("to_date"))
    return conditions


def get_columns():
    return [
        # {
        # 	'fieldname': 'employee_name',
        # 	'fieldtype': 'Data',
        # 	'label': _('Name of Employee'),
        # 	'width': 200,
        # },
        {
            "fieldname": "month_name",
            "fieldtype": "Data",
            "label": _("MONTH"),
            "width": 200,
        },
        {
            "fieldname": "gross_salary",
            "fieldtype": "Currency",
            "label": _("Gross Salary"),
            "width": 150,
        },
        # {
        #     "fieldname": "basic",
        #     "fieldtype": "Currency",
        #     "label": _("Basic Salary"),
        #     "width": 150,
        # },
        {
            "fieldname": "benefits",
            "fieldtype": "Currency",
            "label": _("Benefits -Non- Cash"),
            "width": 150,
        },
        {
            "fieldname": "value_of_quarters",
            "fieldtype": "Currency",
            "label": _("Value of Quarters"),
            "width": 150,
        },
        {
            "fieldname": "basic",
            "fieldtype": "Currency",
            "label": _("Total Gross Pay"),
            "width": 150,
        },
        {
            "fieldname": "def_contr_ret_scheme_e1",
            "fieldtype": "Currency",
            "label": _("Defined 30% of A"),
            "width": 150,
        },
        {
            "fieldname": "def_contr_ret_scheme_e2",
            "fieldtype": "Currency",
            "label": _("Contribution Scheme"),
            "width": 150,
        },
        # {
        #     "fieldname": "nssf_tier_1",
        #     "fieldtype": "Currency",
        #     "label": _("NSSF Tier 1"),
        #     "width": 150,
        # },
        # {
        #     "fieldname": "nssf_tier_2",
        #     "fieldtype": "Currency",
        #     "label": _("NSSF Tier 2"),
        #     "width": 150,
        # },
        # {
        #     "fieldname": "emp_voluntary_nssf",
        #     "fieldtype": "Currency",
        #     "label": _("EMP Voluntary NSSF"),
        #     "width": 150,
        # },
        {
            "fieldname": "def_contr_ret_scheme_e3",
            "fieldtype": "Currency",
            "label": _("Retirement"),
            "width": 150,
        },
        {
            "fieldname": "saving_amount_of_interest",
            "fieldtype": "Currency",
            "label": _("Owner- Occupied Interest"),
            "width": 150,
        },
        {
            "fieldname": "owner_the_lowest_of_e_added",
            "fieldtype": "Currency",
            "label": _("Retirement Contribution & Owner Occupied Interest"),
            "width": 150,
        },
        {
            "fieldname": "charge_pay",
            "fieldtype": "Currency",
            "label": _("Chargeable Pay"),
            "width": 150,
        },
        {
            "fieldname": "tax_charged",
            "fieldtype": "Currency",
            "label": _("Tax Charged"),
            "width": 150,
        },
        {
            "fieldname": "total_relief",
            "fieldtype": "Currency",
            "label": _("Total Relief"),
            "width": 150,
        },
        # {
        #     "fieldname": "personal_relief",
        #     "fieldtype": "Currency",
        #     "label": _("Personal Relief"),
        #     "width": 150,
        # },
        # {
        #     "fieldname": "insurance_relief",
        #     "fieldtype": "Currency",
        #     "label": _("Insurance Relief"),
        #     "width": 150,
        # },
        {
            "fieldname": "paye",
            "fieldtype": "Currency",
            "label": _("PAYE Tax"),
            "width": 150,
        },
        {
            "fieldname": "negative_paye",
            "fieldtype": "Currency",
            "label": _("Negative PAYE"),
            "width": 150,
        },
    ]
