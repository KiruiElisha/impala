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
	data =  frappe.db.sql(""" select  s.transaction_date, s.name  as quotation_no , i.item_code , i.qty , 
		i.amount as amount_exclusive , i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
		i.amount as gp,  s.territory , s.customer_name , s.project , sp.sales_person ,  s.cost_center as division ,
		s.status as status, YEAR(s.transaction_date) as year 
		from `tabQuotation` s
		inner join 	`tabQuotation Item` i  on s.name = i.parent
		inner join `tabSales Team` sp
		where 1=1 order by s.transaction_date desc """.format(conditions), as_dict=1, debug=1)									
	return data


def get_columns(conditions,filters):
	columns = [
		
		{

		"fieldname": "transaction_date",
		"label": _("Date"),
		"fieldtype": "Date",
		"options" : "Quotation",
		"width": 100
	},
	
	
	{

		"fieldname": "quotation_no",
		"label": _("Quotation No"),
		"fieldtype": "Link",
		"options" : "Quotation",
		"width": 150
	},

	
	{

		"fieldname": "item_code",
		"label": _("Item"),
		"fieldtype": "Link",
		"options" : "Item",
		"width": 150
	},

	
	{

		"fieldname": "qty",
		"label": _("Quantity"),
		"fieldtype": "float",
		"width": 100
	},

	
	{

		"fieldname": "amount_exclusive",
		"label": _("Value Exclusive"),
		"fieldtype": "Currency",
		"width": 150
	},


	{

		"fieldname": "status",
		"label": _("Status"),
		"fieldtype": "Data",
		"width": 150
	},


		{

			"fieldname": "sales_person",
			"label": _("Salesmen"),
			"fieldtype": "Link",
			"options" : "Sales Team",
			"width": 100
	}

	]

	return columns

















# # Copyright (c) 2013, Codes Soft and contributors
# # For license information, please see license.txt
# from __future__ import unicode_literals
# from frappe import _
# # from frappe.utils import cstr
# from frappe.utils import getdate, cstr
# import json
# import frappe
# import ast
# from datetime import date
# import datetime
# from dateutil.relativedelta import relativedelta
	 

# from frappe.utils import getdate, cstr
# import json
# import frappe
# from datetime import *
# from dateutil.relativedelta import *
# import calendar
# from datetime import date, timedelta
# from frappe.utils import add_days, getdate, formatdate, nowdate ,  get_first_day, date_diff, add_years  , flt, cint, getdate, now


# def execute(filters=None):
# 	if not filters:
# 		filters = {}
# 	conditions = get_conditions(filters)
# 	data = []
# 	columns = get_columns(conditions ,filters)

# 	period_filters = period_grouping(filters)
# 	period_group_by = period_filters.get("grouping")

# 	period_active_filter = period_filters.get("active_filter")
# 	period_numbering = period_filters.get("numbering")

# 	if filters.get("period"):
# 		master = get_master_data_group(period_active_filter, period_numbering , period_group_by,conditions)
# 		for i in master:
# 			data.append({"period" : i.get("period") , "year" : i.get("year") , "period_no" : i.get("period_no"), "counting" : i.get("counting")})
# 			if period_active_filter == "Week":
# 				start_date = monday_of_calenderweek(i.get("year") ,i.get("period_no") )
# 				end_date = add_days(getdate(start_date), 6);

# 			if period_active_filter == "Month":
# 				start_date = frappe.utils.getdate().replace(year=i.get("year"), month= i.get("period_no"), day=1)
# 				end_date = start_date + timedelta(days=month_range(i.get("year"), i.get("period_no")))

# 			if period_active_filter == "Year":
# 				start_date =  filters.get("from_date")
# 				end_date =  filters.get("from_date")



# 			if period_active_filter == "Year":
# 				start_date =  filters.get("from_date")
# 				end_date =  filters.get("from_date")


# 			child_group = filters.get("grouping")


# 			value =  frappe.db.sql(""" select  s.transaction_date, s.name  as quotation_no , i.item_code , i.qty , 
# 				i.amount as amount_exclusive , i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
# 				i.amount as gp,  s.territory , s.customer_name , s.project , sp.sales_person ,  s.cost_center as division , s.status as status,
# 				YEAR(s.transaction_date) as year  , "{}" as grouping
# 				from `tabQuotation` s
# 				inner join 	`tabQuotation Item` i  on s.name = i.parent
# 				inner join `tabSales Team` sp
# 				where  s.transaction_date >= '{}'  and s.transaction_date <= '{}' {}
# 				""".format(frappe.scrub(child_group) , start_date , end_date , period_group_by ), as_dict=1, debug=1)



# 			if value:
# 				for z in value:
# 					data.append(z)
# 		return columns, data

# 	else:
# 		master = get_master_data(conditions)

# 		for i in master:
# 			data.append(i)
# 		return columns, data



# def get_conditions(filters):
# 	conditions = ""
# 	if filters.get("from_date"):
# 		conditions += " and s.transaction_date >= '{}' ".format(filters.get("from_date"))
# 	if filters.get("to_date"):
# 		conditions += " and s.transaction_date <=  '{}' ".format(filters.get("to_date"))

# 	return conditions




# def get_master_data(conditions = "" ):
# 	data =  frappe.db.sql(""" select  s.transaction_date, s.name  as quotation_no , i.item_code , i.qty , 
# 		i.amount as amount_exclusive , i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
# 		i.amount as gp,  s.territory , s.customer_name , s.project , sp.sales_person  , s.cost_center as division , s.status as status
# 		YEAR(s.transaction_date) as year 
# 		from `tabQuotation` s
# 		inner join 	`tabQuotation Item` i  on s.name = i.parent
# 		inner join `tabSales Team` sp on s.name = sp.parent
# 		where 1=1 {} order by s.transaction_date desc """.format(conditions), as_dict=1, debug=1)									
# 	return data


# def get_master_data_group(active_filter, numbering , group_by, conditions = "" ):
# 	data =  frappe.db.sql(""" select  
# 		s.transaction_date,  
# 		concat('{}', {})  as period , {}  as period_no,
# 		YEAR(s.transaction_date) as year 
# 		from `tabQuotation` s
# 		inner join 	`tabQuotation Item` i  on s.name = i.parent
# 		inner join `tabSales Team` sp 
# 		on s.name = sp.parent
# 		where 1=1 {} {}		
# 		""".format(active_filter ,  numbering , numbering , conditions , group_by), as_dict=1, debug=1)									
# 	return data



# def get_data(conditions = "" ):
# 	data =  frappe.db.sql(""" select  s.transaction_date, s.name  as quotation_no , i.item_code , i.qty , 
# 		i.amount as amount_exclusive , i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
# 		i.amount as gp,  s.territory , s.customer_name , s.project , sp.sales_person ,  s.cost_center as division , s.status as status
# 		YEAR(s.transaction_date) as year 
# 		from `tabQuotation` s
# 		inner join 	`tabQuotation Item` i  on s.name = i.parent
# 		inner join `tabSales Team` sp
# 		where 1=1 order by s.transaction_date desc """.format(conditions), as_dict=1, debug=1)									
# 	return data






# def get_columns(conditions,filters):
# 	columns = []

# 	columns.append(
# 	{

# 		"fieldname": "transaction_date",
# 		"label": _("Date"),
# 		"fieldtype": "Date",
# 		"options" : "Quotation",
# 		"width": 100
# 	})
	
# 	columns.append(
# 	{

# 		"fieldname": "quotation_no",
# 		"label": _("Quotation No"),
# 		"fieldtype": "Link",
# 		"options" : "Quotation",
# 		"width": 150
# 	})

# 	columns.append(
# 	{

# 		"fieldname": "item_code",
# 		"label": _("Item"),
# 		"fieldtype": "Link",
# 		"options" : "Item",
# 		"width": 150
# 	})
# 	columns.append(
# 	{

# 		"fieldname": "qty",
# 		"label": _("Quantity"),
# 		"fieldtype": "float",
# 		"width": 100
# 	})
# 	columns.append(
# 	{

# 		"fieldname": "amount_exclusive",
# 		"label": _("Value Exclusive"),
# 		"fieldtype": "Currency",
# 		"width": 150
# 	})

# 	columns.append(
# 	{

# 		"fieldname": "status",
# 		"label": _("Status"),
# 		"fieldtype": "Data",
# 		"width": 150
# 	})
# 	columns.append(
# 		{

# 			"fieldname": "sales_person",
# 			"label": _("Salesmen"),
# 			"fieldtype": "Link",
# 			"options" : "Sales Team",
# 			"width": 100
# 	})
	
	
	
	
# 	return columns








# def period_grouping(filters):
# 	active_filter = ""
# 	grouping = ""
# 	numbering = ""
# 	sorting = ""


# 	if filters.get("period") and filters.get("grouping"):
# 		if filters.get("period")=='Week':
# 			grouping += "group by  WEEK(s.transaction_date),  YEAR(s.transaction_date)"
# 			sorting += "ORDER BY s.transaction_date asc"
# 			numbering = "WEEK(s.transaction_date)"

# 		if filters.get("period")=='Month':
# 			grouping +=  "group by MONTH(s.transaction_date),  YEAR(s.transaction_date) ORDER BY s.transaction_date asc "
# 			sorting += "ORDER BY s.transaction_date asc"
# 			numbering = "MONTH(s.transaction_date)"

# 		if filters.get("period")=='Year':
# 			grouping +=  "group by YEAR(s.transaction_date) ORDER BY s.transaction_date asc "
# 			sorting += "ORDER BY s.transaction_date asc"
# 			numbering = "YEAR(s.transaction_date)"

# 		if filters.get("grouping")=='Item':
# 			grouping += ", i.item_code "
# 			sorting += ", i.item_code "

# 		if filters.get("grouping")=='Sales Person':
# 			grouping += ", sp.sales_person "
# 			sorting += ", sp.sales_person"

# 		if filters.get("grouping")=='Customer':
# 			grouping += ", s.customer_name "
# 			sorting += ", s.customer_name "

# 		if filters.get("grouping")=='Item Group':
# 			grouping += ", i.item_group "
# 			sorting += ", i.item_group "

# 		if filters.get("grouping")=='Territory':
# 			grouping += ", s.territory "
# 			sorting += ", s.territory "

# 		if filters.get("grouping")=='Division':
# 			grouping += ", s.cost_center "
# 			sorting += ", i.cost_center "

# 	return  { "grouping" : grouping , "active_filter" : filters.get("period") , "numbering" : numbering  }



# @frappe.whitelist()
# def month_range(year, month):
# 	return calendar.monthrange(year, month)[1]


# @frappe.whitelist()
# def monday_of_calenderweek(year = 2020,week = 1):
#     year = int(year)
#     week = int(week)
#     first = date(year, 1, 1)

#     base = 1 if first.isocalendar()[1] == 1 else 8
#     return first + timedelta(days=base - first.isocalendar()[2] + 7 * (week - 1))

