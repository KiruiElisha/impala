# Copyright (c) 2013, Codes Soft and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr
from frappe.desk.reportview import build_match_conditions
from collections import defaultdict
import frappe

def execute(filters=None):
	columns = get_columns()
	data = []





	master = frappe.db.sql(""" SELECT so.customer_name , so.transaction_date, so.status,ti.item_code,ti.item_name,ti.item_group,ti.additional_notes from `tabSales Order` so inner join `tabSales Order Items` ti where 1=1""",as_dict = 1,debug = 1)

	row = {}	

	#loop for populate row in columns
	for i  in master:

		row["customer_name"] = i.get('customer_name')
		row["order_type"] = i.get('order_type')
		row["transaction_date"] = i.get('transaction_date')
		row["status"] = i.get('status')
		row["item_name"] = i.get('item_name')
		row["item_code"] = i.get('item_code')
		row["item_group"] = i.get('item_group')
		row["additional_notes"] = i.get('additional_notes')



		data.append(row)







	
	return columns, data
	frapp.msgprint(cstr(data))


def get_columns():
    columns = [

		{
			"fieldname":"item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 150,
		},	
		{
			"fieldname":"item_code",
			"label": _("Item Code"),
			"fieldtype": "Data",
			"width": 150,
		},	
		{
			"fieldname":"item_group",
			"label": _("Item Group"),
			"fieldtype": "Link",
			"width": 150,
			"options": "Item Group"
		},
		{
			"fieldname":"customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"width": 150,
		},	
		{
			"fieldname":"status",
			"label": _("Status"),
			"fieldtype": "Link",
			"option" : "status",
			"width": 150,
		},	
		{
			"fieldname":"additional_notes",
			"label": _("Additional Notes"),
			"fieldtype": "Small Text",
			"width": 150,
		},	
			
		{
			"fieldname":"transaction_date",
			"label": _("Transactions Date"),
			"fieldtype": "Date",
			"width": 150,
		}
    ]
    return columns


# Copyright (c) 2013, Codes Soft and contributors
# For license information, please see license.txt

# import frappe

def execute(filters=None):
	columns = get_columns()
	data = []





	master = frappe.db.sql(""" SELECT so.customer_name , so.transaction_date, so.status,ti.item_code,ti.item_name,ti.item_group,ti.additional_notes from `tabSales Order Item` so inner join `tabitems` ti where 1=1""",as_dict = 1,debug = 1)

	row = {}	

	#loop for populate row in columns
	for i  in master:

		row["customer_name"] = i.get('customer_name')
		row["order_type"] = i.get('order_type')
		row["transaction_date"] = i.get('transaction_date')
		row["status"] = i.get('status')
		row["item_name"] = i.get('item_name')
		row["item_code"] = i.get('item_code')
		row["item_group"] = i.get('item_group')
		row["additional_notes"] = i.get('additional_notes')



		data.append(row)







	
	return columns, data
	frapp.msgprint(cstr(data))


def get_columns():
    columns = [

		{
			"fieldname": "item_name",
			"label": _("Item_Name"),
			"fieldtype": "Data",
			"width": 150,
		},	
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Data",
			"width": 150,
		},	
		{
			"fieldname": "item_group",
			"label": _("Item Group"),
			"fieldtype": "Link",
			"width": 150,
			"options": "Item Group"
		},
		{
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"width": 150,
		},	
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Link",
			"option" : "status",
			"width": 150,
		},	
		{
			"fieldname": "additional_notes",
			"label": _("Additional Notes"),
			"fieldtype": "Small Text",
			"width": 150,
		},	
			
		{
			"fieldname": "transaction_date",
			"label": _("Transactions Date"),
			"fieldtype": "Date",
			"width": 150,
		}
    ]
    return columns


