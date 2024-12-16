# Copyright (c) 2013, Codes Soft and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from frappe import _
# from frappe.utils import cstr
from frappe.utils import getdate, cstr
import json
import frappe
import ast
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
	 

from frappe.utils import getdate, cstr
import json
import frappe
from datetime import *
from dateutil.relativedelta import *
import calendar
from datetime import date, timedelta
from frappe.utils import add_days, getdate, formatdate, nowdate ,  get_first_day, date_diff, add_years  , flt, cint, getdate, now


def execute(filters=None):
	if not filters:
		filters = {}



	# range_grouping = range_grouping(filters)


	conditions = get_conditions(filters)
	columns = get_columns()

	data  = get_data_normal(conditions = conditions )


	return columns , data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.transaction_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and s.transaction_date <=  '{}' ".format(filters.get("to_date"))

	if filters.get("company"):
		conditions += " and s.company =  '{}' ".format(filters.get("company"))



	if filters.get("status")  and filters.get("status") != "":
		conditions += " and s.status =  '{}' ".format(filters.get("status"))

	if filters.get("item_code") and filters.get("item_code") != "":
		conditions += " and i.item_code =  '{}' ".format(filters.get("item_code"))

	if filters.get("item_group") and filters.get("item_group") != "":
		conditions += " and i.item_group =  '{}' ".format(filters.get("item_group"))



	return conditions






def get_data_normal(conditions   = "", filters = ""):
		data =  frappe.db.sql(""" select  s.transaction_date, i.item_code , sum(i.qty)  as qty,  


			i.item_code , i.item_name ,  i.item_group ,   

			IF(s.tax_type= 'Exclusive', sum((i.amount *  i.total_tax_percentage  / 100) + i.amount)  , sum(i.amount)  ) amount_exclusive , 

			IF(s.tax_type= 'Inclusive',   sum(i.amount -  (i.amount *  i.total_tax_percentage  / 100))   ,  0  ) amount_inclusive , 

			(select sum(b.valuation_rate) from `tabBin` b where b.item_code = i.item_code) item_cost 



			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent		
			inner join `tabSales Team` sp on s.name = sp.parent			
			where 1=1 {}  group by s.transaction_date   order by s.transaction_date desc , i.item_code asc """.format(conditions ), as_dict=1, debug=1)
		return data



def get_columns():
	columns = []

	columns.append(
	{
	"fieldname": "transaction_date",
	"label": _("Date"),
	"fieldtype": "Date",
	"width": 100
	})

	columns.append(
	{
	"fieldname": "item_code",
	"label": _("Item"),
	"fieldtype": "Link",
	"options" : "Item",
	"width": 150
	})

	columns.append(
	{
		"fieldname": "item_name",
		"label": _("Item Name"),
		"fieldtype": "Data",
		"width": 150
	})

	columns.append(
	{

		"fieldname": "item_group",
		"label": _("Item Group"),
		"fieldtype": "Link",
		"options" : "Item",
		"width": 150
	})




	columns.append(
	{
	"fieldname": "qty",
	"label": _("Qty"),
	"options" : "Float",
	"width": 150
	})





	columns.append(
	{
	"fieldname": "amount_inclusive",
	"label": _("Amount Inlusive"),
	"options" : "Currency",
	"width": 150
	})


	columns.append(
	{
	"fieldname": "amount_exclusive",
	"label": _("Amount Exlusive"),
	"options" : "Currency",
	"width": 150
	})






	return columns






@frappe.whitelist()
def month_range(year, month):
	return calendar.monthrange(year, month)[1]



def get_month_name(num):
	months_name = {1 : "Jan",2 : "Feb",3 : "Mar",4 : "Apr",5 : "May",6 : "June",7 : "July",8 : "Aug",9 : "Sept",10 : "Oct",11 : "Nov",12 : "Dec"}
	return months_name.get(num)
