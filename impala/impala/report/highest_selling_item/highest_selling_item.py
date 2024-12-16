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
	master_data = get_data(conditions , filters )
	data = []

	if master_data:
		for z in master_data:
			data.append(z)
	return columns, data




def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.posting_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and s.posting_date <=  '{}' ".format(filters.get("to_date"))



	if filters.get("item_code"):
		conditions += " and i.item_code = '{}' ".format(filters.get("item_code"))
	if filters.get("item_group"):
		conditions += " and i.item_group =  '{}' ".format(filters.get("item_group"))


	if filters.get("cost_center"):
		conditions += " and s.cost_center =  '{}' ".format(filters.get("cost_center"))



	return conditions


def get_data(conditions = ""  , filters = {}):

	if filters.get("top"):
		if filters.get("top") != "":
			top = str(filters.get("top"))
			data =  frappe.db.sql(""" select  
				i.item_code ,  i.item_name , i.item_group ,  sum(i.qty) as qty , 
				sum(i.rate) as item_value,  
				s.cost_center as division 
				from `tabSales Invoice` s
				inner join 	`tabSales Invoice Item` i  on s.name = i.parent
				inner join `tabSales Team` sp
				where 1=1  {} group by i.item_code  order by s.posting_date desc ,  sum(i.rate) desc ,    i.item_code ,  s.cost_center
				limit {};
				 """.format(conditions  , top), as_dict=1, debug=1)									
	else:
		data =  frappe.db.sql(""" select  
			i.item_code ,  i.item_name , i.item_group ,  sum(i.qty) as qty , 
			sum(i.rate) as item_value,  
			s.cost_center as division 
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent
			inner join `tabSales Team` sp
			where 1=1  {} group by i.item_code  order by s.posting_date desc ,    i.item_code ,  s.cost_center
			
			 """.format(conditions), as_dict=1, debug=1)									

	return data



def get_columns(conditions,filters):
	columns = [
	{

		"fieldname": "item_code",
		"label": _("Item"),
		"fieldtype": "Link",
		"options" : "Item",
		"width": 150
	},



	{

		"fieldname": "item_name",
		"label": _("Item Name"),
		"fieldtype": "Data",
		"width": 150
	},



	{

		"fieldname": "item_group",
		"label": _("Item Group"),
		"fieldtype": "Link",
		"options" : "Item Group",
		"width": 150
	},



	{
		"fieldname": "item_value",
		"label": _("Item Value"),
		"fieldtype": "Currency",
		"width": 150
	},


	{

		"fieldname": "qty",
		"label": _("Quantity"),
		"fieldtype": "float",
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









