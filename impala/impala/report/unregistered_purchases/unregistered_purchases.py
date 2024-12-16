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
        row["supplier_name"] = d.get("supplier_name")
        row["total"] = d.get("total")

        data.append(row)
    return columns, data


def get_columns():

    columns = [
        {
            "fieldname": "supplier_name",
            "label": _("supplier name"),
            "fieldtype": "Data",
            "options": "Purchase Invoice",
            "width": 400,
        },
        {
            "fieldname": "total",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "options": "Purchase Invoice",
            "width": 200,
        },
    ]

    return columns


def get_data(conditions):

    # data = frappe.db.sql("""select s.supplier as supplier, SUM(s.total) as total
    # 	 	from `tabPurchase Invoice` s
    # 		inner join `tabSupplier` c on s.Supplier = c.name
    # 		where s.docstatus=1 and c.unregistered=1 {} group by s.Supplier order by 1""".format(conditions), as_dict=1)

    data = frappe.db.sql(
        """select s.supplier_name as supplier_name, SUM(i.base_net_amount) as total 
		 	from `tabPurchase Invoice` s 
			inner join `tabPurchase Invoice Item` i on s.name = i.parent
			inner join `tabSupplier` c on s.supplier = c.name
			where s.docstatus=1 and c.unregistered=1 and i.item_tax_template NOT IN ('Zero Rated - IG', 'Zero Rated - IAL','Exempt - IG','Exempt - IAL') {} group by s.supplier order by 1""".format(
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
