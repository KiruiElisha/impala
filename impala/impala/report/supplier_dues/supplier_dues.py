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
	data =  frappe.db.sql(""" select  p.transaction_date, p.name  as voucher_no, p.supplier, p.grand_total,
		p.rounded_total, advance_paid, i.cost_center as division, i.item_code , i.qty
		from `tabPurchase Order` p
		inner join 	`tabPurchase Order Item` i  on p.name = i.parent
		where 1=1 order by p.transaction_date desc """.format(conditions), as_dict=1, debug=1)									
	return data



def get_columns(conditions,filters):
	columns = [
		{

			"fieldname": "supplier",
			"label": _("Supplie"),
			"fieldtype": "Data",
			"width": 100
		},
		{

			"fieldname": "transaction_date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{

			"fieldname": "grand_total",
			"label": _("Grand Total"),
			"options" : "Purchase Order",
			"fieldtype": "Currency",
			"width": 150
		},

		{

			"fieldname": "rounded_total",
			"label": _("Rounded Total"),
			"options" : "Purchase Order",
			"fieldtype": "Currency",
			"width": 150
		},
		{

			"fieldname": "advance_paid",
			"label": _("Advance Paid"),
			"options" : "Purchase Order",
			"fieldtype": "Currency",
			"width": 150
		}
	]

	return columns
