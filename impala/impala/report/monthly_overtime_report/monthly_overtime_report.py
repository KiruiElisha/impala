from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    conditions = get_conditions(filters)
    columns = get_column(filters, conditions)
    data = []

    master = get_details(conditions, filters)
    employees = frappe.db.sql("SELECT name, employee_name, department FROM `tabEmployee` WHERE status='Active' %s" % conditions, as_dict=True)

    if master and employees:
        for emp in employees:
            row = {
                "name": emp.name,
                "employee_name": emp.employee_name,
                "department": emp.department,
                "manual_overtime_in_minutes": "0:00",
                "holiday_overtime_in_minutes": "0:00",
                "fixed_overtime_in_minutes": "0:00",
            }

            emp_overtime_cond = ""
            if filters.year:
                from_date = "{}-01-01".format(filters.year)
                to_date = "{}-12-31".format(filters.year)
                emp_overtime_cond += " AND eovt.payroll_date >= '{}'".format(from_date)
                emp_overtime_cond += " AND eovt.payroll_date <= '{}'".format(to_date)

            emp_ovt_query = frappe.db.sql("""
                SELECT eovt.salary_component, DATE_FORMAT(eovt.payroll_date, '%b') as month,
                SUM(eovt_details.overtime_in_mins) AS overtime_in_mins
                FROM `tabEmployee Overtime` eovt
                RIGHT JOIN `tabOvertime Details` eovt_details ON eovt.name = eovt_details.parent
                WHERE eovt.docstatus=1 AND eovt_details.employee='{}' {} GROUP BY eovt.salary_component, month
                """.format(emp.name, emp_overtime_cond), as_dict=True)

            for month in [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]:
                row["manual_overtime_in_minutes_month_{}".format(month)] = "0:00"
                row["holiday_overtime_in_minutes_month_{}".format(month)] = "0:00"
                row["fixed_overtime_in_minutes_month_{}".format(month)] = "0:00"

            for eovt in emp_ovt_query:
                month_name = eovt.month
                minutes = eovt.overtime_in_mins or 0
                formatted_time = format_minutes_as_hours_and_minutes(minutes)

                if eovt.salary_component == 'Manual OverTime':
                    row["manual_overtime_in_minutes_month_{}".format(month_name)] = formatted_time
                    row["manual_overtime_in_minutes"] = add_formatted_time(row["manual_overtime_in_minutes"], minutes)
                elif eovt.salary_component == 'Fixed OverTime':
                    row["fixed_overtime_in_minutes_month_{}".format(month_name)] = formatted_time
                    row["fixed_overtime_in_minutes"] = add_formatted_time(row["fixed_overtime_in_minutes"], minutes)
                elif eovt.salary_component == 'Holiday OverTime':
                    row["holiday_overtime_in_minutes_month_{}".format(month_name)] = formatted_time
                    row["holiday_overtime_in_minutes"] = add_formatted_time(row["holiday_overtime_in_minutes"], minutes)

            data.append(row)

    return columns, data


def format_minutes_as_hours_and_minutes(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return "{:02}:{:02}".format(int(hours), int(remaining_minutes))


def add_formatted_time(existing_time, minutes_to_add):
    existing_hours, existing_minutes = map(float, existing_time.split(':'))
    total_minutes = existing_hours * 60 + existing_minutes + minutes_to_add
    return format_minutes_as_hours_and_minutes(total_minutes)


def get_column(filters, conditions):
    columns = [
        {
            "fieldname": "name",
            "label": _("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 100
        },
        {
            "fieldname": "employee_name",
            "label": _("Employee Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "manual_overtime_in_minutes",
            "label": _("Total Manual overtime"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "holiday_overtime_in_minutes",
            "label": _("Total Holiday overtime"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "fixed_overtime_in_minutes",
            "label": _("Total Fixed overtime"),
            "fieldtype": "Data",
            "width": 80
        },
    ]

    # Dynamically add columns for each month
    for month in [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]:
        columns.append(
            {
                "fieldname": "manual_overtime_in_minutes_month_{}".format(month),
                "label": _("Manual overtime ({})".format(month)),
                "fieldtype": "Data",
                "width": 80,
            }
        )
        columns.append(
            {
                "fieldname": "holiday_overtime_in_minutes_month_{}".format(month),
                "label": _("Holiday overtime ({})".format(month)),
                "fieldtype": "Data",
                "width": 80,
            }
        )
        columns.append(
            {
                "fieldname": "fixed_overtime_in_minutes_month_{}".format(month),
                "label": _("Fixed overtime ({})".format(month)),
                "fieldtype": "Data",
                "width": 80,
            }
        )

    return columns


def get_details(conditions="", filters={}):
    data = frappe.db.sql("""
        SELECT e.name, e.employee_name, c.status, DATE_FORMAT(c.attendance_date, '%b') as month, COUNT(c.name) as count
        FROM `tabEmployee` e
        INNER JOIN `tabAttendance` c ON c.employee = e.name
        WHERE e.status = 'Active' AND c.docstatus = 1 {} GROUP BY e.employee, c.status, month
        ORDER BY e.employee_name, c.status, month
    """.format(conditions), as_dict=True)

    return data


def get_conditions(filters):
    conditions = ""
    if filters.get("department"):
        conditions += " AND e.department = '{}'".format(filters.get("department"))
    if filters.get("designation"):
        conditions += " AND e.designation = '{}'".format(filters.get("designation"))
    if filters.get("employee"):
        conditions += " AND e.name = '{}'".format(filters.get("employee"))
    if filters.get("cost_center"):
        conditions += " AND e.cost_center = '{}'".format(filters.get("cost_center"))
    if filters.get("branch"):
        conditions += " AND e.branch = '{}'".format(filters.get("branch"))
    if filters.get("time_table"):
        conditions += " AND c.employee_shift = '{}'".format(filters.get("time_table"))

    return conditions
