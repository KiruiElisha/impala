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
# import pandas as pd
# from fiscalyear import *


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
		conditions += " and m.transaction_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and m.transaction_date <=  '{}' ".format(filters.get("to_date"))

	return conditions


def get_data(conditions = "" ):
	data =  frappe.db.sql(""" SELECT m.name as name, m.transaction_date as transaction_date,
	i.item_code as item_code, i.stock_qty as stock_avail_qty, i.ordered_qty as ordered_qty, i.actual_qty as qty_under_prod
	FROM `tabMaterial Request` m 
	INNER JOIN `tabMaterial Request Item` i ON m.name = i.parent
	WHERE 1=1 {}""".format(conditions), as_dict=1, debug=1)								
	
	return data



def get_columns(conditions,filters):
	columns = [
		{

			"fieldname": "name",
			"label": _("MR Number"),
			"fieldtype": "Link",
			"options": "Material Request",
			"width": 150
		},
		{

			"fieldname": "transaction_date",
			"label": _("Date"),
			"fieldtype": "Date",
			"options": "Material Request",
			"width": 150
		},
		{

			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Material Request Item",
			"width": 150
		},

		{

			"fieldname": "stock_avail_qty",
			"label": _("Stock Avail Qty"),
			"fieldtype": "float",
			"options": "Material Request Item",
			"width": 100
		},

		{

			"fieldname": "ordered_qty",
			"label": _("Ordered Qty"),
			"fieldtype": "float",
			"options": "Material Request Item",
			"width": 100
		},

		{

			"fieldname": "qty_under_prod",
			"label": _("Qty under Production"),
			"fieldtype": "float",
			"width": 100
		}
		
	]

	return columns
