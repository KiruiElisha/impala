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
	
	
	

	for d in master:
		row ={}
		row.update(d)
		remaining_qty = int(row.get("total_qty")) - int(row.get("delivered_qty")) 
		row["remaining_qty"] = remaining_qty
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

	if filters.get("department"):
		conditions += " and department =  '{}' ".format(filters.get("department"))
	return conditions



def get_data(conditions):

	data =  frappe.db.sql(""" select  so.title,so.customer,so.customer_name, 
	oi.item_code,oi.item_name,so.status,so.order_type,oi.produced_qty,oi.delivered_qty,
	so.set_warehouse,so.company,oi.qty, so.transaction_date, so.delivery_date,so.department,so.total_qty,oi.supplier
	from `tabSales Order` so   inner join  `tabSales Order Item` oi on so.name = oi.parent where 1=1 {} """.format(conditions), as_dict=1, debug=1)	
								
	return data

def get_columns(conditions,filters):
	columns = [
		{
			"fieldname": "title",
			"label": _("Title"),
			"fieldtype": "Data",
			"width": 150
		},
				{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},	
		{
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"width": 150
		},	
		
		
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 150
		},
		{	
			"fieldname": "transaction_date",
			"label": _("Planned Start Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{	
			"fieldname": "delivery_date",
			"label": _("Expected Delivery Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "order_type",
			"label": _("Order Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "set_warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
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
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},{
			"fieldname": "item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 150
		},

		{
			"fieldname": "produced_qty",
			"label": _("Produced Qty"),
			"fieldtype": "Float",

			"width": 150
		},
		{
			"fieldname": "delivered_qty",
			"label": _("Delivered Qty"),
			"fieldtype": "Float",
			"width": 150
		},

		{
			"fieldname": "remaining_qty",
			"label": _("Remaining Qty"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "qty",
			"label": _("Qty"),
			"fieldtype": "Float",
			"width": 150
		},

		
		{
			"fieldname": "total_qty",
			"label": _("Total Qty"),
			"fieldtype": "Float",
			"width": 150
		},	
		{
			"fieldname": "department",
			"label": _("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": 150
		},
		
		{
			"fieldname": "supplier",
			"label": _("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150
		},

	]

	return columns