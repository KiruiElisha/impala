# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	conditions = get_conditions(filters)
	columns, data = get_columns(), get_data(filters, conditions)
	return columns, data




def get_data(filters, conditions):
	
	data = frappe.db.sql(""" 
		SELECT
			so.customer, so.name as sales_order, soi.item_name, soi.ordered_qty, soi.produced_qty,
			soi.delivered_qty as dispatched_qty,
			(SELECT parent FROM `tabDelivery Note Item` WHERE `tabDelivery Note Item`.against_sales_order=so.name LIMIT 1) AS delivery_note,
			(SELECT parent FROM `tabSales Invoice Item` WHERE `tabSales Invoice Item`.sales_order = so.name LIMIT 1) AS invoice_number,
			IF((SELECT name FROM `tabPacking Slip` WHERE `tabPacking Slip`.delivery_note = (SELECT parent FROM `tabDelivery Note Item`
			 WHERE `tabDelivery Note Item`.against_sales_order=so.name LIMIT 1) LIMIT 1) IS NOT NULL, "<input type='checkbox' checked>", "<input type='checkbox'>") as is_packed
			
		FROM
		`tabSales Order` so
		INNER JOIN 
		`tabSales Order Item` soi ON soi.parent = so.name
		WHERE so.docstatus=1
		{}
		""".format(conditions), as_dict=True, debug=False)

	return data





def get_conditions(filters):
	conditions = ""

	if filters.company:
		conditions += " and so.company = '{}'".format(filters.company)
	if filters.date_range:
		conditions += " and so.transaction_date BETWEEN '{}' AND '{}'".format(filters.date_range[0], filters.date_range[1])
	if filters.customer:
		conditions += " and so.customer = '{}'".format(filters.customer)
	if filters.item:
		conditions += " and soi.item_code = '{}'".format(filters.item)
	return conditions



def get_columns():
	columns = [
		{	
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},
		{	
			"label": _("Sales Order"),
			"fieldname": "sales_order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 150
		},
		{	
			"label": _("Item"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 220
		},
		{	
			"label": _("Order Qty"),
			"fieldname": "ordered_qty",
			"fieldtype": "Float",
			"width": 150
		},
		{	
			"label": _("Produced Qty"),
			"fieldname": "produced_qty",
			"fieldtype": "Float",
			"width": 150
		},
		{	
			"label": _("Dispatched Qty"),
			"fieldname": "dispatched_qty",
			"fieldtype": "Float",
			"width": 150
		},
		{	
			"label": _("DN Number"),
			"fieldname": "delivery_note",
			"fieldtype": "Link",
			"options": "Delivery Note",
			"width": 150
		},
		{	
			"label": _("Invoice Number"),
			"fieldname": "invoice_number",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 150
		},
		{	
			"label": _("Packed YES/NO"),
			"fieldname": "is_packed",
			"fieldtype": "HTML",
			"width": 100,
		},

	]

	return columns
