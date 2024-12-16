# Copyright (c) 2013, Codes Soft and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from frappe import _
# from frappe.utils import cstr
from frappe.utils import getdate, cstr
import json
import frappe

def execute(filters=None):
	if not filters:
		filters = {}

	
	conditions = get_conditions(filters)
	columns = get_columns(conditions ,filters)

	master = get_data(conditions)
	data = []
	#greet = frappe.msgprint("Hello Test Message! ")
	#frappe.db.delete('Spider Sales Invoice', 'Mr XYZ')
	
	

	for d in master:
		row ={}
		row.update(d)
		# row['production_item'] = d.get('production_item')
		# row['status'] = d.get('status')
		# row['produced_qty'] = d.get('produced_qty')
		# row['sales_order'] = d.get('sales_order')
		# row['description'] = d.get('description')
		# row["company"] = d.get('company')
		# row['qty'] = d.get('qty')
		# row['planned_start_date'] = d.get('planned_start_date')
		# row['expected_delivery_date'] = d.get('expected_delivery_date')
		data.append(row)

	return columns, data


def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and company = '{}' ".format(filters.get("company"))
	
	if filters.get("from_date"):
		conditions += " and planned_start_date >= '{}' ".format(filters.get("from_date"))

	if filters.get("to_date"):
		conditions += " and planned_start_date <=  '{}' ".format(filters.get("to_date"))
	return conditions



def get_data(conditions):

	data =  frappe.db.sql(""" select production_item, status, produced_qty, sales_order,company, qty, planned_start_date, expected_delivery_date
							 from `tabWork Order` where 1=1 {}  """.format(conditions), as_dict=1, debug=1)	
								
	return data

def get_columns(conditions,filters):
	columns = [
		{
			"fieldname": "production_item",
			"label": _("Production Item"),
			"fieldtype": "Link",
			"options": "item",
			"width": 150
		},
				{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"options": "status",
			"width": 150
		},	
		{
			"fieldname": "produced_qty",
			"label": _("Manufactured Qty"),
			"fieldtype": "Float",
			"options": "Spider Sales Invoice",
			"width": 150
		},	
		{
			"fieldname": "sales_order",
			"label": _("Sales Order"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 150
		},
		{
			"fieldname": "company",
			"label": _("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"width": 150
		},
		{
			"fieldname": "qty",
			"label": _("Qty To Manufacture"),
			"fieldtype": "Float",
			"width": 150
		},
		{	
			"fieldname": "planned_start_date",
			"label": _("Planned Start Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{	
			"fieldname": "expected_delivery_date",
			"label": _("Expected Delivery Date"),
			"fieldtype": "Date",
			"width": 150
		},

	]

	return columns