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
# from fiscalyear import *


def execute(filters=None):
	if not filters:
		filters = {}
	conditions = get_conditions(filters)
	columns = get_columns(conditions ,filters)
	# data = get_data(conditions)
	data = []
	master = get_master(conditions)
	values = []

	for i in master:
		data.append({"month_name" : i.get("month_name") + " "+ str(i.get("year"))   })

		values = frappe.db.sql(""" select MONTH(s.posting_date) as month,  MONTHNAME(s.posting_date) as month_name  ,  

			i.item_code , i.item_name ,  i.item_group ,   

			IF(s.tax_type= 'Exclusive', sum((i.amount *  i.total_tax_percentage  / 100) + i.amount)  , sum(i.amount)  ) amount_exclusive , 

			IF(s.tax_type= 'Inclusive',   sum(i.amount -  (i.amount *  i.total_tax_percentage  / 100))   ,  0  ) amount_inclusive , 


			(select sum(b.valuation_rate) from `tabBin` b where b.item_code = i.item_code) item_cost , 




			SUM(i.qty) as qty 
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent
			inner join `tabSales Team` sp
			where 1=1 {} and  MONTH(s.posting_date) = '{}' GROUP BY i.item_code  , MONTH(s.posting_date) 
			order by s.posting_date desc """.format(conditions , i.get("month") ), as_dict=1, debug=1)
		for v in values:
			row = {
				"item_code" :  v.get("item_code"),
				"item_name" :  v.get("item_name"),
				"item_group" :  v.get("item_group"),
				"qty" :  v.get("qty"),
				"amount_exclusive" :  v.get("amount_exclusive"),
				"amount_inclusive" :  v.get("amount_inclusive"),
			}
			data.append(row)


	# frappe.msgprint(cstr(values))
	return columns, data




def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.posting_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and s.posting_date <=  '{}' ".format(filters.get("to_date"))

	if filters.get("status")  and filters.get("status") != "":
		conditions += " and s.status =  '{}' ".format(filters.get("status"))
	if filters.get("item_code") and filters.get("item_code") != "":
		conditions += " and i.item_code =  '{}' ".format(filters.get("item_code"))


	if filters.get("item_group") and filters.get("item_group") != "":
		conditions += " and i.item_group =  '{}' ".format(filters.get("item_group"))


	if filters.get("company"):
		conditions += " and s.company =  '{}' ".format(filters.get("company"))

	return conditions


def get_data(conditions = "" ):
	data =  frappe.db.sql(""" select MONTH(s.posting_date) as month,  MONTHNAME(s.posting_date) as month_name  ,  
		
		i.item_code , i.item_name ,  i.item_group ,   

		SUM(i.qty) as qty , 
		SUM(i.amount) as amount_exclusive , 
		i.amount as item_cost,  SUM(i.amount) as amount_inclusive  
		from `tabSales Order` s
		inner join 	`tabSales Order Item` i  on s.name = i.parent
		inner join `tabSales Team` sp
		where 1=1 {} GROUP BY i.item_code  , MONTH(s.posting_date) order by s.posting_date desc """.format(conditions), as_dict=1, debug=1)									
	return data



def get_master(conditions = "" ):
	data =  frappe.db.sql(""" select MONTH(s.posting_date) as month , MONTHNAME(s.posting_date) as month_name ,    YEAR(s.posting_date) as year		
		from `tabSales Invoice` s
		inner join 	`tabSales Invoice Item` i  on s.name = i.parent
		inner join `tabSales Team` sp
		where 1=1 {} GROUP BY MONTH(s.posting_date)  , YEAR(s.posting_date)  order by s.posting_date desc """.format(conditions), as_dict=1, debug=1)									
	return data


def get_columns(conditions,filters):
	columns = [

		{

			"fieldname": "month_name",
			"label": _("Month Name"),
			"fieldtype": "Data",
			"width": 250
		},

	
		{

			"fieldname": "item_code",
			"label": _("Item"),
			"fieldtype": "Link",
			"options" : "Item",
			"width": 150
		},


		{

			"fieldname": "item_group",
			"label": _("Item Group"),
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

			"fieldname": "qty",
			"label": _("Monthly Qty"),
			"fieldtype": "Float",
			"width": 100
		},

		{
			"fieldname": "amount_exclusive",
			"label": _("Monthly Value Exclusive"),
			"fieldtype": "Currency",
			"width": 150
		},
	
		{
			"fieldname": "amount_inclusive",
			"label": _("Monthly Value Inclusive"),
			"fieldtype": "Currency",
			"width": 150
		} , 


		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "data",
			"width": 150
		}
	]

	return columns








@frappe.whitelist()
def month_range(year, month):
	return calendar.monthrange(year, month)[1]



def get_month_name(num):
	months_name = {1 : "Jan",2 : "Feb",3 : "Mar",4 : "Apr",5 : "May",6 : "June",7 : "July",8 : "Aug",9 : "Sept",10 : "Oct",11 : "Nov",12 : "Dec"}
	return months_name.get(num)
