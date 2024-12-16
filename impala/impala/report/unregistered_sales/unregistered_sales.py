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
        row["customer_name"] = d.get("customer_name")
        row["total"] = d.get("total")

        data.append(row)
    return columns, data


def get_columns():

    columns = [
        {
            "fieldname": "customer_name",
            "label": _("customer name"),
            "fieldtype": "Data",
            "options": "Sales Invoice",
            "width": 400,
        },
        {
            "fieldname": "total",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "options": "Sales Invoice Item",
            "width": 200,
        },
    ]

    return columns


def get_data(conditions):

    # data = frappe.db.sql(
    #     """select s.customer_name as customer_name, SUM(s.grand_total) as total
    #         from `tabSales Invoice` s
    #         inner join `tabSales Invoice Item` i on s.name = i.parent
    #         inner join `tabCustomer` c on s.customer = c.name
    #         where s.docstatus=1 and c.unregistered=1 and i.item_tax_template NOT IN ('Zero Rated - IG', 'Zero Rated - IAL','Exempt - IG','Exempt - IAL') {} group by s.customer order by 1""".format(
    #         conditions
    #     ),
    #     as_dict=1,
    # )

    data = frappe.db.sql(
        """select s.customer_name as customer_name, SUM(i.base_net_amount) as total
        from `tabSales Invoice` s
        left join `tabSales Invoice Item` i on s.name = i.parent and i.item_tax_template NOT IN ('Zero Rated - IG', 'Zero Rated - IAL','Exempt - IG','Exempt - IAL')
        inner join `tabCustomer` c on s.customer = c.name and c.unregistered=1
        where s.docstatus=1 {} group by s.customer order by 1""".format(
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
    if filters.get("customer"):
        conditions += " and s.customer =  '{}' ".format(filters.get("customer"))
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
