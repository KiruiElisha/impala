# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, getdate

def execute(filters=None):
	columns, data = [], []
	if not filters:
		filters = {}

	master_conditions = get_master_conditions(filters)
	conditions = get_conditions(filters)
	master_query = get_data(filters, master_conditions)
	columns = get_columns(master_query)
	data = []

	row1={"description": "<b>Sales<b>"}
	
	for profile in master_query:
		sales_data = frappe.db.sql(""" select SUM(grand_total) as sales_amount from `tabSales Invoice`
			where docstatus=1 and is_return=0 and pos_profile='{}' {}""".format(profile[0], conditions), as_dict=1)

		for d in sales_data:			
			row1[frappe.scrub(profile[0])] = d.get("sales_amount") or 0.0
		
	data.append(row1)

	row2={}
	row2["description"] = "<b>Return</b>"
	for profile in master_query:
		return_data = frappe.db.sql(""" select SUM(grand_total) as return_amount from `tabSales Invoice`
			where docstatus=1 and is_return=1 and pos_profile='{}' {}""".format(profile[0], conditions), as_dict=1)

		for r in return_data:
			row2[frappe.scrub(profile[0])] = r.get("return_amount") or 0.0

	data.append(row2)
	
	row3 = {}
	row3["description"] = "<b>Net</b>"
	for profile in master_query:
		sales_data = frappe.db.sql(""" select SUM(grand_total) as sales_amount from `tabSales Invoice`
			where docstatus=1 and is_return=0 and pos_profile='{}' {}""".format(profile[0], conditions), as_dict=1)

		return_data = frappe.db.sql(""" select SUM(grand_total) as return_amount from `tabSales Invoice`
			where docstatus=1 and is_return=1 and pos_profile='{}' {}""".format(profile[0], conditions), as_dict=1)

		for d in sales_data:			
			sales_amount = d.get("sales_amount") or 0.0

		for r in return_data:
			return_amount = r.get("return_amount") or 0.0

		row3[frappe.scrub(profile[0])] = sales_amount + return_amount

	data.append(row3)

	row4 = {}
	row4["description"] = "<b>Payment Methods</b>"
	data.append(row4)

	payment_modes = frappe.db.get_list('Mode of Payment')
	for mode in payment_modes:		 
		row_mode = {}
		row_mode["description"] = "<b>"+mode+"</b>"
		data.append(row_mode)

	return columns, data



def get_columns(master_query):
	columns = [

		{
			"fieldname": "description",
			"label": _("POS Sales"),
			"fieldtype": "Data",
			"width": 260
		},
	]

	for profile in master_query:
		columns.append(
			{
				"fieldname": frappe.scrub(profile[0]),
				"label": profile[0],
				"fieldtype": "Currency",
			},
		)

	return columns



def get_data(filters, conditions):

	data = frappe.db.sql(""" select distinct name from `tabPOS Profile` where 1=1 {}""".format(conditions), as_list=1)
	return data


def get_master_conditions(filters):
	conditions = ""
	if filters.get("company"):
		" and company='{}'".format(filters.get("company"))
	if filters.get("pos_profile"):
		" and name='{}'".format(filters.get("pos_profile"))

	return conditions


def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		" and company='{}'".format(filters.get("company"))
	if filters.get("pos_profile"):
		" and pos_profile='{}'".format(filters.get("pos_profile"))

	return conditions