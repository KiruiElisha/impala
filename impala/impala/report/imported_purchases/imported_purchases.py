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

        row["type"] = "Import"
        row["pin_no"] = d.get("pin_no")
        row["supplier"] = d.get("supplier")
        row["supp_inv"] = d.get("supp_inv")
        row["supp_inv_date"] = d.get("supp_inv_date")
        row["shipment_no"] = d.get("shipment_no")
        row["description"] = d.get("description")
        row["tims_cu_no"] = d.get("tims_cu_no")
        # row["doctype"] = "Purchase Invoice"
        if d.is_return == 1:
            row["base_net_amount"] = -abs(d.get("base_net_amount") / 0.16) or None
        else:
            row["base_net_amount"] = (d.get("base_net_amount") / 0.16) or None
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
            "label": _("Pin of Supplier"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 200,
        },
        {
            "fieldname": "supplier",
            "label": _("Supplier Name"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 150,
        },
        # {
        # 	"fieldname": "etr_sno",
        # 	"label": _("etr serial no"),
        # 	"fieldtype": "Data",
        # 	"options": "Purchase Invoice",
        # 	"width": 150
        # },
        {
            "fieldname": "supp_inv",
            "label": _("Supplier Invoice"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {
            "fieldname": "supp_inv_date",
            "label": _("Supplier Invoice Date"),
            "fieldtype": "Date",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {
            "fieldname": "shipment_no",
            "label": _("Shipment No"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {
            "fieldname": "description",
            "label": _("Description"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
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
            "label": _("Amount Excl."),
            "fieldtype": "Currency",
            "options": "Purchase Invoice",
            "width": 150,
        },
    ]

    return columns


def get_data(conditions):

    data = frappe.db.sql(
        """select s.tims_cu_no as tims_cu_no, s.bill_no as supp_inv, s.bill_date as supp_inv_date, s.shipment_no as shipment_no, c.local_and_international as local_and_international, c.tax_id as pin_no, s.supplier as supplier, s.posting_date as posting_date, s.name as name,
			s.description as description, s.return_against return_against, s.is_return as is_return, (select posting_date from `tabPurchase Invoice` where name=s.return_against) as cnote_date,
			s.taxes_and_charges_added as base_net_amount 
		 	from `tabPurchase Invoice` s 
			inner join `tabSupplier` c on s.supplier = c.name
			where s.docstatus=1 and c.unregistered=0 and c.import=1 {} order by s.posting_date DESC""".format(
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
