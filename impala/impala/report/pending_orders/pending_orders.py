# Copyright (c) 2013, Codes Soft and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from frappe import _
# from frappe.utils import cstr
from frappe.utils import getdate, cstr, add_days, formatdate, nowdate, get_first_day, date_diff, add_years  , flt, cint, now
import json
import frappe
import ast
import datetime
from datetime import *
from dateutil.relativedelta import *
import calendar
import pandas as pd
from fiscalyear import *


def execute(filters=None):
	if not filters:
		filters = {}
	conditions = get_conditions(filters)
	columns = get_columns(conditions ,filters)
	master_data = get_data(conditions)
	data = []

	if master_data:
		for z in master_data:
			data.append(z)
	return columns, data




def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.transaction_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and s.transaction_date <=  '{}' ".format(filters.get("to_date"))

	return conditions


def get_data(conditions = "" ):
	data =  frappe.db.sql(""" select i.item_code, i.ordered_qty , i.work_order_qty, i.produce, 
		i.delivered_qty, i.item_group,
		i.amount as amount_exclusive , i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
		i.amount as gp,  s.territory , s.customer , s.project , sp.sales_person ,  s.cost_center as division , s.status as status,
		YEAR(s.transaction_date) as year 
		from `tabSales Order` s
		inner join 	`tabSales Order Item` i  on s.name = i.parent
		inner join `tabSales Team` sp
		where 1=1 {} order by s.customer""".format(conditions), as_dict=1, debug=1)									
	return data




def get_columns(conditions,filters):

	columns = [
		{

			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options" : "Customer",
			"width": 150
		},

		{
			"fieldname": "item_code",
			"label": _("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},

		{

			"fieldname": "work_order_qty",
			"label": _(" Item under Prod Qty "),
			"fieldtype": "Int",
			"options": "Sales Order Item",
			"width": 150
		},

		{

			"fieldname": "produce",
			"label": _("Item Produced"),
			"options" : "Sales Order Item",
			"fieldtype": "Int",
			"width": 150
		},

		{

			"fieldname": "delivered_qty",
			"label": _("Item Dispatched"),
			"options" : "Sales Order Item",
			"fieldtype": "Int",
			"width": 150
		},

		{

			"fieldname": "pending_item",
			"label": _("Item Pending"),
			"fieldtype": "Int",
			"width": 150
		},

		{

			"fieldname": "division",
			"label": _("Division"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 150
		}
	]

	return columns


