# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
from frappe.utils import cstr, getdate


def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    conditions = get_conditions(filters)
    query_data = get_data(conditions)
    data = []

    for d in query_data:
        row = {}

        row["type"] = "Local"
        row["pin_no"] = d.get("pin_no")
        row["supplier_name"] = d.get("supplier_name")
        row["etr_sno"] = frappe.db.get_value(
            "Company", filters.company, "etr_serial_no"
        )
        row["supp_inv_date"] = d.get("supp_inv_date")
        row["supp_inv"] = d.get("supp_inv")
        row["doctype"] = "Purchase Invoice"
        row["tims_cu_no"] = d.get("tims_cu_no")
        if d.is_return == 1:
            row["base_net_amount"] = -abs(d.get("base_net_amount"))
        else:
            row["base_net_amount"] = d.get("base_net_amount")

        row["blank"] = ""
        row["return_against"] = d.get("return_against")
        row["cnote_date"] = d.get("cnote_date")
        data.append(row)

    return columns, data


def get_columns():

    columns = [
        {
            "fieldname": "type",
            "label": _("Type of Purchase"),
            "fieldtype": "Data",
            "options": "Supplier",
            "width": 200,
        },
        {
            "fieldname": "pin_no",
            "label": _("Pin No"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 200,
        },
        {
            "fieldname": "supplier_name",
            "label": _("supplier name"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {
            "fieldname": "etr_sno",
            "label": _("etr serial no"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {
            "fieldname": "supp_inv_date",
            "label": _("date"),
            "fieldtype": "Date",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {
            "fieldname": "supp_inv",
            "label": _("inv no"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {
            "fieldname": "doctype",
            "label": _("doc type"),
            "fieldtype": "Data",
            "options": "Doctype",
            "width": 150,
        },
        {
            "fieldname": "tims_cu_no",
            "label": _("TIMS CU No"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "base_net_amount",
            "label": _("amount excl"),
            "fieldtype": "Currency",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {
            "fieldname": "blank",
            "label": _("blank"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {
            "fieldname": "return_against",
            "label": _("credit note allocation"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {
            "fieldname": "cnote_date",
            "label": _("cnote date"),
            "fieldtype": "Date",
            "options": "Purchase Invoice",
            "width": 150,
        },
    ]

    return columns


def get_data(conditions):
    data = frappe.db.sql(
        """select s.tims_cu_no as tims_cu_no, s.bill_no as supp_inv, s.bill_date as supp_inv_date, c.local_and_international as local_and_international, c.tax_id as pin_no, s.supplier_name as supplier_name, s.posting_date as posting_date, s.name as name,
			s.return_against return_against, s.is_return as is_return, (select posting_date from `tabPurchase Invoice` where name=s.return_against) as cnote_date,
			SUM(i.base_net_amount) as base_net_amount  
		 	from `tabPurchase Invoice` s 
			inner join `tabPurchase Invoice Item` i on s.name = i.parent
			inner join `tabSupplier` c on s.supplier = c.name
			where s.docstatus=1 and c.local_and_international='Local' and c.unregistered=0 and c.import=0 and i.total_tax_percentage= '16%' {} group by s.name order by s.posting_date DESC""".format(
            conditions
        ),
        as_dict=1,
    )
    return data


def get_conditions(filters):
    conditions = ""
    if filters.get("company"):
        conditions += " and s.company =  '{}' ".format(filters.get("company"))
    if filters.get("cost_center"):
        conditions += " and s.cost_center =  '{}' ".format(filters.get("cost_center"))
    if filters.get("supplier"):
        conditions += " and s.supplier =  '{}' ".format(filters.get("supplier"))
    if filters.get("month"):
        conditions += " and MONTHNAME(s.posting_date) = '{}' ".format(
            filters.get("month")
        )
    if filters.get("fiscal_year"):
        fyr_start_date = frappe.db.get_value(
            "Fiscal Year", filters.get("fiscal_year"), "year_start_date"
        )
        fiscal_year = getdate(fyr_start_date).year
        conditions += " and YEAR(s.posting_date) =  '{}' ".format(fiscal_year)

    return conditions
