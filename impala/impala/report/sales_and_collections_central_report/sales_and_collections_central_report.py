# Copyright (c) 2022, Codes Soft and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, today
import datetime


def execute(filters=None):
    select_group = ""
    groupby = ""
    group_doctype = "Department"
    select_details = "name as details"
    select_group = "department as details"
    groupby = "GROUP BY department ORDER BY department"
    group_doctype = "Department"
    data = []
    columns = get_columns()
    conditions = get_conditions_for_department(filters)
    daily_sales = get_daily_sales_for_department(select_group, conditions, groupby)
    weekly_sales = get_weekly_sales_for_department(select_group, conditions, groupby)
    monthly_sales = get_monthly_sales_for_department(select_group, conditions, groupby)
    daily_collections = get_daily_collections_for_department(
        select_group, conditions, groupby
    )
    weekly_collections = get_weekly_collections_for_department(
        select_group, conditions, groupby
    )
    monthly_collections = get_monthly_collections_for_department(
        select_group, conditions, groupby
    )
    master_for_department = get_details_for_department(select_details, group_doctype)
    row = {}
    row["report_name"] = "<h5><b>Sales and Collections by Department</b></h5>"
    row["details"] = ""
    row["daily_sales"] = ""
    row["weekly_sales"] = ""
    row["monthly_sales"] = ""
    row["daily_collections"] = ""
    row["weekly_collections"] = ""
    row["monthly_collections"] = ""
    data.append(row)
    for d in master_for_department:
        row = {}
        row["report_name"] = ""
        row["details"] = d.get("details")
        for ds in daily_sales:
            if ds.get("details") == d.get("details"):
                row["daily_sales"] = ds.get("sales") or 00
        for ws in weekly_sales:
            if ws.get("details") == d.get("details"):
                row["weekly_sales"] = ws.get("sales") or 00
        for ms in monthly_sales:
            if ms.get("details") == d.get("details"):
                row["monthly_sales"] = ms.get("sales") or 00

        for dc in daily_collections:
            if dc.get("details") == d.get("details"):
                row["daily_collections"] = dc.get("collection") or 00
        for wc in weekly_collections:
            if wc.get("details") == d.get("details"):
                row["weekly_collections"] = wc.get("collection") or 00
        for mc in monthly_collections:
            if mc.get("details") == d.get("details"):
                row["monthly_collections"] = mc.get("collection") or 00
        data.append(row)
    row = {}
    row["report_name"] = ""
    row["details"] = ""
    row["daily_sales"] = ""
    row["weekly_sales"] = ""
    row["monthly_sales"] = ""
    row["daily_collections"] = ""
    row["weekly_collections"] = ""
    row["monthly_collections"] = ""
    data.append(row)
    row = {}
    row["report_name"] = "<h5>Report Name</h5>"
    row["details"] = "<h5>Divisions</h5>"
    row["daily_sales"] = ""
    row["weekly_sales"] = ""
    row["monthly_sales"] = ""
    row["daily_collections"] = ""
    row["weekly_collections"] = ""
    row["monthly_collections"] = ""
    data.append(row)
    row = {}
    row["report_name"] = "<h5><b>Sales and Collections by Division</b></h5>"
    row["details"] = ""
    row["daily_sales"] = ""
    row["weekly_sales"] = ""
    row["monthly_sales"] = ""
    row["daily_collections"] = ""
    row["weekly_collections"] = ""
    row["monthly_collections"] = ""
    data.append(row)
    select_group = ""
    groupby = ""
    select_details = "name as details"
    select_group = "cost_center as details"
    groupby = "GROUP BY cost_center ORDER BY cost_center"
    group_doctype = "Cost Center"
    conditions = get_conditions_for_division(filters)
    daily_sales = get_daily_sales_for_division(select_group, conditions, groupby)
    weekly_sales = get_weekly_sales_for_division(select_group, conditions, groupby)
    monthly_sales = get_monthly_sales_for_division(select_group, conditions, groupby)
    daily_collections = get_daily_collections_for_division(
        select_group, conditions, groupby
    )
    weekly_collections = get_weekly_collections_for_division(
        select_group, conditions, groupby
    )
    monthly_collections = get_monthly_collections_for_division(
        select_group, conditions, groupby
    )
    master_for_division = get_details_for_division(
        select_details, group_doctype, filters
    )
    for d in master_for_division:
        row = {}
        row["report_name"] = ""
        row["details"] = d.get("details")
        for ds in daily_sales:
            if ds.get("details") == d.get("details"):
                row["daily_sales"] = ds.get("sales") or 00
        for ws in weekly_sales:
            if ws.get("details") == d.get("details"):
                row["weekly_sales"] = ws.get("sales") or 00
        for ms in monthly_sales:
            if ms.get("details") == d.get("details"):
                row["monthly_sales"] = ms.get("sales") or 00
        for dc in daily_collections:
            if dc.get("details") == d.get("details"):
                row["daily_collections"] = dc.get("collection") or 00
        for wc in weekly_collections:
            if wc.get("details") == d.get("details"):
                row["weekly_collections"] = wc.get("collection") or 00
        for mc in monthly_collections:
            if mc.get("details") == d.get("details"):
                row["monthly_collections"] = mc.get("collection") or 00
        data.append(row)
    row = {}
    row["report_name"] = ""
    row["details"] = ""
    row["daily_sales"] = ""
    row["weekly_sales"] = ""
    row["monthly_sales"] = ""
    row["daily_collections"] = ""
    row["weekly_collections"] = ""
    row["monthly_collections"] = ""
    data.append(row)
    row = {}
    row["report_name"] = "<h5>Report Name</h5>"
    row["details"] = "<h5>Salesman</h5>"
    row["daily_sales"] = ""
    row["weekly_sales"] = ""
    row["monthly_sales"] = ""
    row["daily_collections"] = ""
    row["weekly_collections"] = ""
    row["monthly_collections"] = ""
    data.append(row)
    row = {}
    row["report_name"] = "<h5><b>Sales and Collections by Salesmen</b></h5>"
    row["details"] = ""
    row["daily_sales"] = ""
    row["weekly_sales"] = ""
    row["monthly_sales"] = ""
    row["daily_collections"] = ""
    row["weekly_collections"] = ""
    row["monthly_collections"] = ""
    data.append(row)
    select_group = ""
    groupby = ""
    group_doctype = "Sales Person"
    select_details = "name as details"
    select_group = "st.sales_person as details"
    groupby = "GROUP BY st.sales_person ORDER BY st.sales_person"
    conditions = get_conditions_for_salesmen(filters)
    daily_sales = get_daily_sales_for_salesmen(select_group, conditions, groupby)
    weekly_sales = get_weekly_sales_for_salesmen(select_group, conditions, groupby)
    monthly_sales = get_monthly_sales_for_salesmen(select_group, conditions, groupby)
    conditions = get_conditions2_for_salesmen(filters)
    daily_collections = get_daily_collections_for_salesmen(conditions, groupby)
    weekly_collections = get_weekly_collections_for_salesmen(conditions, groupby)
    monthly_collections = get_monthly_collections_for_salesmen(conditions, groupby)
    master_for_salesmen = get_details_for_salesmen(
        select_details, group_doctype, filters
    )
    for d in master_for_salesmen:
        row = {}
        row["report_name"] = ""
        row["details"] = d.get("details")
        for ds in daily_sales:
            if ds.get("details") == d.get("details"):
                row["daily_sales"] = ds.get("sales") or 00
        for ws in weekly_sales:
            if ws.get("details") == d.get("details"):
                row["weekly_sales"] = ws.get("sales") or 00
        for ms in monthly_sales:
            if ms.get("details") == d.get("details"):
                row["monthly_sales"] = ms.get("sales") or 0.0
        for dc in daily_collections:
            if dc.get("details") == d.get("details"):
                row["daily_collections"] = dc.get("collection") or 00
        for wc in weekly_collections:
            if wc.get("details") == d.get("details"):
                row["weekly_collections"] = wc.get("collection") or 0.0
        for mc in monthly_collections:
            if mc.get("details") == d.get("details"):
                row["monthly_collections"] = mc.get("collection") or 0.0
        data.append(row)

    row = {}
    row["report_name"] = ""
    row["details"] = ""
    row["daily_sales"] = ""
    row["weekly_sales"] = ""
    row["monthly_sales"] = ""
    row["daily_collections"] = ""
    row["weekly_collections"] = ""
    row["monthly_collections"] = ""
    data.append(row)
    row = {}
    row["report_name"] = "<h5>Report Name</h5>"
    row["details"] = "<h5>Customer Group</h5>"
    row["daily_sales"] = ""
    row["weekly_sales"] = ""
    row["monthly_sales"] = ""
    row["daily_collections"] = ""
    row["weekly_collections"] = ""
    row["monthly_collections"] = ""
    data.append(row)
    row = {}
    row["report_name"] = "<h5><b>Sales and Collections by Customer Group</b></h5>"
    row["details"] = ""
    row["daily_sales"] = ""
    row["weekly_sales"] = ""
    row["monthly_sales"] = ""
    row["daily_collections"] = ""
    row["weekly_collections"] = ""
    row["monthly_collections"] = ""
    data.append(row)
    select_group = ""
    groupby = ""
    group_doctype = "Customer Group"
    select_details = "name as details"
    select_group = "customer_group as details"
    groupby = "GROUP BY customer_group ORDER BY customer_group"
    group_doctype = "Customer Group"
    conditions = get_conditions_for_customer_group(filters)
    daily_sales = get_daily_sales_for_customer_group(select_group, conditions, groupby)
    weekly_sales = get_weekly_sales_for_customer_group(
        select_group, conditions, groupby
    )
    monthly_sales = get_monthly_sales_for_customer_group(
        select_group, conditions, groupby
    )
    select_group = "customer_group as details"
    groupby = "GROUP BY cs.customer_group ORDER BY cs.customer_group"
    group_doctype = "Customer Group"
    conditions = get_conditions2_for_customer_group(filters)
    daily_collections = get_daily_collections_for_customer_group(conditions, groupby)
    weekly_collections = get_weekly_collections_for_customer_group(conditions, groupby)
    monthly_collections = get_monthly_collections_for_customer_group(
        conditions, groupby
    )
    master_for_customer_group = get_details_for_customer_group(
        select_details, group_doctype, filters
    )
    for d in master_for_customer_group:
        row = {}
        row["details"] = d.get("details")
        for ds in daily_sales:
            if ds.get("details") == d.get("details"):
                row["daily_sales"] = ds.get("sales") or 0.0
        for ws in weekly_sales:
            if ws.get("details") == d.get("details"):
                row["weekly_sales"] = ws.get("sales") or 0.0
        for ms in monthly_sales:
            if ms.get("details") == d.get("details"):
                row["monthly_sales"] = ms.get("sales") or 0.0

        for dc in daily_collections:
            if dc.get("details") == d.get("details"):
                row["daily_collections"] = dc.get("collection") or 0.0
        for wc in weekly_collections:
            if wc.get("details") == d.get("details"):
                row["weekly_collections"] = wc.get("collection") or 0.0
        for mc in monthly_collections:
            if mc.get("details") == d.get("details"):
                row["monthly_collections"] = mc.get("collection") or 0.0
        data.append(row)

    return columns, data


def get_conditions_for_department(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and company = '{}'".format(filters.get("company"))
    if filters.get("from_date"):
        conditions += " and posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and posting_date <= '{}'".format(filters.get("to_date"))

    return conditions


def get_details_for_department(select_details, group_doctype):
    details = frappe.db.sql(
        """SELECT {} FROM `tab{}`
			WHERE disabled=0""".format(
            select_details, group_doctype
        ),
        as_dict=1,
        debug=True,
    )

    return details


def get_daily_sales_for_department(select_group, conditions, groupby):

    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and posting_date= '{}' {} {}""".format(
            select_group, today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_weekly_sales_for_department(select_group, conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]
    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and WEEK(posting_date)='{}' {} {}""".format(
            select_group, current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_monthly_sales_for_department(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")
    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and MONTHNAME(posting_date)='{}' {} {}""".format(
            select_group, current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_daily_collections_for_department(select_group, conditions, groupby):

    collections = frappe.db.sql(
        """ SELECT {}, SUM(paid_amount) as collection
		FROM `tabPayment Entry`
		WHERE docstatus=1 and posting_date='{}' {} {}""".format(
            select_group, today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_weekly_collections_for_department(select_group, conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]

    collections = frappe.db.sql(
        """ SELECT {}, SUM(paid_amount) as collection
		FROM `tabPayment Entry`
		WHERE docstatus=1 and WEEK(posting_date)='{}' {} {}""".format(
            select_group, current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_monthly_collections_for_department(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")

    collections = frappe.db.sql(
        """ SELECT {}, SUM(paid_amount) as collection
		FROM `tabPayment Entry`
		WHERE docstatus=1 and MONTHNAME(posting_date)='{}' {} {}""".format(
            select_group, current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_columns():
    dept_div_label = "Department"
    # if filters.get("groupby") == "Department":
    #     dept_div_label = "Department"
    # if filters.get("groupby") == "Division":
    #     dept_div_label = "Division"

    columns = [
        {
            "fieldname": "report_name",
            "label": "Report Name",
            "fieldtype": "Data",
            "width": 280,
            "text-align": "left",
        },
        {
            "fieldname": "details",
            "label": _(dept_div_label),
            "fieldtype": "Data",
            "width": 250,
            "text-align": "left",
        },
        {
            "fieldname": "daily_sales",
            "label": _("Daily Sales"),
            "fieldtype": "Currency",
            "width": 150,
            "default": 0,
        },
        {
            "fieldname": "daily_collections",
            "label": _("Daily Collection"),
            "fieldtype": "Currency",
            "width": 150,
            "default": 0,
        },
        {
            "fieldname": "weekly_sales",
            "label": _("Weekly Sales"),
            "fieldtype": "Currency",
            "width": 150,
            "default": 0,
        },
        {
            "fieldname": "weekly_collections",
            "label": _("Weekly Collection"),
            "fieldtype": "Currency",
            "width": 150,
            "default": 0,
        },
        {
            "fieldname": "monthly_sales",
            "label": _("Monthly Sales"),
            "fieldtype": "Currency",
            "width": 150,
            "default": 0,
        },
        {
            "fieldname": "monthly_collections",
            "label": _("Monthly Collection"),
            "fieldtype": "Currency",
            "width": 150,
            "default": 0,
        },
    ]

    return columns


def get_conditions_for_division(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and company = '{}'".format(filters.get("company"))
    if filters.get("from_date"):
        conditions += " and posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and posting_date <= '{}'".format(filters.get("to_date"))

    return conditions


def get_details_for_division(select_details, group_doctype, filters):
    details = frappe.db.sql(
        """SELECT {} FROM `tab{}`
			WHERE disabled=0""".format(
            select_details, group_doctype
        ),
        as_dict=1,
        debug=True,
    )

    return details


def get_daily_sales_for_division(select_group, conditions, groupby):

    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and posting_date= '{}' {} {}""".format(
            select_group, today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_weekly_sales_for_division(select_group, conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]
    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and WEEK(posting_date)='{}' {} {}""".format(
            select_group, current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_monthly_sales_for_division(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")
    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and MONTHNAME(posting_date)='{}' {} {}""".format(
            select_group, current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_daily_collections_for_division(select_group, conditions, groupby):

    collections = frappe.db.sql(
        """ SELECT {}, SUM(paid_amount) as collection
		FROM `tabPayment Entry`
		WHERE docstatus=1 and posting_date='{}' {} {}""".format(
            select_group, today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_weekly_collections_for_division(select_group, conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]

    collections = frappe.db.sql(
        """ SELECT {}, SUM(paid_amount) as collection
		FROM `tabPayment Entry`
		WHERE docstatus=1 and WEEK(posting_date)='{}' {} {}""".format(
            select_group, current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_monthly_collections_for_division(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")

    collections = frappe.db.sql(
        """ SELECT {}, SUM(paid_amount) as collection
		FROM `tabPayment Entry`
		WHERE docstatus=1 and MONTHNAME(posting_date)='{}' {} {}""".format(
            select_group, current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_conditions_for_salesmen(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and sl.company = '{}'".format(filters.get("company"))
    # if filters.get("customer_groups"):
    # 	conditions += " and customer_group = '{}'".format(filters.get("customer_groups"))
    if filters.get("from_date"):
        conditions += " and sl.posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and sl.posting_date <= '{}'".format(filters.get("to_date"))
    return conditions


def get_conditions2_for_salesmen(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and pe.company = '{}'".format(filters.get("company"))
    if filters.get("sales_person"):
        conditions += " and st.name = '{}'".format(filters.get("sales_person"))
    if filters.get("from_date"):
        conditions += " and pe.posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and pe.posting_date <= '{}'".format(filters.get("to_date"))

    return conditions


def get_details_for_salesmen(select_details, group_doctype, filters):
    details = frappe.db.sql(
        """SELECT {} FROM `tab{}`""".format(select_details, group_doctype),
        as_dict=1,
        debug=True,
    )
    return details


def get_daily_sales_for_salesmen(select_group, conditions, groupby):

    sales = frappe.db.sql(
        """SELECT {}, SUM(sl.grand_total) as sales
			FROM `tabSales Invoice` sl inner join `tabSales Team` st on sl.name = st.parent
			WHERE sl.docstatus=1 and sl.posting_date='{}' {} {}""".format(
            select_group, today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_weekly_sales_for_salesmen(select_group, conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]
    sales = frappe.db.sql(
        """SELECT {}, SUM(sl.grand_total) as sales
			FROM `tabSales Invoice` sl inner join `tabSales Team` st on sl.name = st.parent
			WHERE sl.docstatus=1 and WEEK(sl.posting_date)='{}' {} {}""".format(
            select_group, current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_monthly_sales_for_salesmen(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")
    sales = frappe.db.sql(
        """SELECT {}, SUM(sl.grand_total) as sales
			FROM `tabSales Invoice` sl inner join `tabSales Team` st on sl.name = st.parent
			WHERE sl.docstatus=1 and MONTHNAME(sl.posting_date)='{}' {} {}""".format(
            select_group, current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_daily_collections_for_salesmen(conditions, groupby):

    collections = frappe.db.sql(
        """ SELECT sales_person as details, SUM(pe.paid_amount) as collection
		FROM `tabPayment Entry` pe inner join `tabPayment Entry Reference` per on  pe.name = per.parent
		inner join `tabSales Invoice` si on  per.reference_name = si.name
  		inner join `tabSales Team` st on si.name = st.parent
		WHERE pe.docstatus=1 and pe.payment_type='Receive' and pe.posting_date='{}' {} {}""".format(
            today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_weekly_collections_for_salesmen(conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]
    collections = frappe.db.sql(
        """ SELECT sales_person as details, SUM(pe.paid_amount) as collection
		FROM `tabPayment Entry` pe inner join `tabPayment Entry Reference` per on  pe.name = per.parent
		inner join `tabSales Invoice` si on  per.reference_name = si.name
  		inner join `tabSales Team` st on si.name = st.parent
		WHERE pe.docstatus=1 and pe.payment_type='Receive' and WEEK(pe.posting_date)='{}' {} {}""".format(
            current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_monthly_collections_for_salesmen(conditions, groupby):
    current_month = datetime.date.today().strftime("%B")

    collections = frappe.db.sql(
        """
                            SELECT sales_person as details, SUM(pe.paid_amount) as collection
		FROM `tabPayment Entry` pe inner join `tabPayment Entry Reference` per on  pe.name = per.parent
		inner join `tabSales Invoice` si on  per.reference_name = si.name
  		inner join `tabSales Team` st on si.name = st.parent
		WHERE pe.docstatus=1 and pe.payment_type='Receive' and MONTHNAME(pe.posting_date)='{}' {} {}""".format(
            current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_conditions2_for_customer_group(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and pe.company = '{}'".format(filters.get("company"))
    if filters.get("customer_groups"):
        conditions += " and cs.customer_group = '{}'".format(
            filters.get("customer_groups")
        )
    if filters.get("from_date"):
        conditions += " and pe.posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and pe.posting_date <= '{}'".format(filters.get("to_date"))

    return conditions


def get_conditions_for_customer_group(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " and company = '{}'".format(filters.get("company"))
    if filters.get("customer_groups"):
        conditions += " and customer_group = '{}'".format(
            filters.get("customer_groups")
        )
    if filters.get("from_date"):
        conditions += " and posting_date >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        conditions += " and posting_date <= '{}'".format(filters.get("to_date"))

    return conditions


def get_details_for_customer_group(select_details, group_doctype, filters):
    details = frappe.db.sql(
        """SELECT {} FROM `tab{}` """.format(select_details, group_doctype),
        as_dict=1,
        debug=True,
    )
    return details


def get_daily_sales_for_customer_group(select_group, conditions, groupby):

    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and posting_date= '{}' {} {}""".format(
            select_group, today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_weekly_sales_for_customer_group(select_group, conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]
    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and WEEK(posting_date)='{}' {} {}""".format(
            select_group, current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_monthly_sales_for_customer_group(select_group, conditions, groupby):
    current_month = datetime.date.today().strftime("%B")
    sales = frappe.db.sql(
        """SELECT {}, SUM(grand_total) as sales
			FROM `tabSales Invoice`
			WHERE docstatus=1 and MONTHNAME(posting_date)='{}' {} {}""".format(
            select_group, current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return sales


def get_daily_collections_for_customer_group(conditions, groupby):

    collections = frappe.db.sql(
        """ SELECT pe.party, customer_group as details, SUM(pe.paid_amount) as collection
		FROM `tabPayment Entry` pe inner join `tabCustomer` cs on  pe.party = cs.customer_code
		WHERE pe.docstatus=1 and pe.posting_date='{}' {} {}""".format(
            today(), conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_weekly_collections_for_customer_group(conditions, groupby):
    current_week = datetime.date.today().isocalendar()[1]
    collections = frappe.db.sql(
        """ SELECT pe.party, customer_group as details, SUM(pe.paid_amount) as collection
		FROM `tabPayment Entry` pe inner join `tabCustomer` cs on  pe.party = cs.customer_code
		WHERE pe.docstatus=1 and WEEK(pe.posting_date)='{}' {} {}""".format(
            current_week, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections


def get_monthly_collections_for_customer_group(conditions, groupby):
    current_month = datetime.date.today().strftime("%B")

    collections = frappe.db.sql(
        """
                            SELECT pe.party, customer_group as details, SUM(pe.paid_amount) as collection
		FROM `tabPayment Entry` pe inner join `tabCustomer` cs on  pe.party = cs.customer_code
		WHERE pe.docstatus=1 and MONTHNAME(pe.posting_date)='{}' {} {}""".format(
            current_month, conditions, groupby
        ),
        as_dict=1,
        debug=True,
    )

    return collections
