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
	data =  frappe.db.sql(""" select  s.transaction_date, s.name  as voucher_no , i.item_code , i.qty , 
		i.amount as amount_exclusive , i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
		i.amount as gp,  s.territory , s.customer , s.project , sp.sales_person , td.target_amount, s.cost_center as division , s.status as status
		from `tabSales Order` s
		inner join 	`tabSales Order Item` i  on s.name = i.parent
		inner join `tabSales Team` sp on s.name = sp.parent
		inner join `tabTarget Detail` td on sp.name = td.parent 
		where 1=1 {} order by s.transaction_date desc """.format(conditions), as_dict=1, debug=1)									
	return data


def get_columns(conditions,filters):
	columns = [
	
		{

			"fieldname": "transaction_date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100
		},

		{

			"fieldname": "item_code",
			"label": _("Item"),
			"fieldtype": "Link",
			"options" : "Item",
			"width": 150
		},

		{

			"fieldname": "sales_person",
			"label": _("Sales Person"),
			"fieldtype": "Data",
			"options" : "Item",
			"width": 100
		},

		{

			"fieldname": "target_amount",
			"label": _("Target Amount"),
			"options" : "Target Detail",
			"fieldtype": "Data",
			"width": 100
		},

		{

			"fieldname": "target_acieved",
			"label": _("Target Achieved"),
			"options" : "Target Detail",
			"fieldtype": "Data",
			"width": 100
		},
		{

			"fieldname": "target_acieved_perc",
			"label": _("Target Achieved %"),
			"options" : "Target Detail",
			"fieldtype": "Data",
			"width": 100
		},

		{

			"fieldname": "target_var",
			"label": _("Target Variance"),
			"options" : "Target Detail",
			"fieldtype": "Data",
			"width": 100
		},
	
		{

			"fieldname": "target_var_perc",
			"label": _("Target Variance %"),
			"options" : "Target Detail",
			"fieldtype": "Data",
			"width": 100
		},

		{

			"fieldname": "division",
			"label": _("Cost Center"),
			"options" : "Cost Center",
			"fieldtype": "Link",
			"width": 100
		}
	]

	return columns


