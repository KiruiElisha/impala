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
	conditions = get_conditions(filters)
	conditions_2 = get_conditions_2(filters)

	data = []
	new_column = []
	map_group = {}


	columns = get_columns(conditions , filters)


	ranging_group = range_grouping(filters) 


	if filters.get("range"):
		level_1 = get_group_range(conditions = conditions , filters = filters , ranging_group = ranging_group )

		# frappe.msgprint(cstr(level_1))

		# frappe.msgprint("Level 1 and level 2 and level 3 ")
		for i in level_1:
			start_date = ""
			end_date = ""
			data.append({"period" : i.get("period") }) 
			if i.get("period_name") == "Week":
				start_date = monday_of_calenderweek(i.get("year") ,i.get("numbering") )
				end_date = add_days(getdate(start_date), 6);

			if i.get("period_name") == "Month":
				start_date = frappe.utils.getdate().replace(year=i.get("year"), month= i.get("numbering"), day=1)
				end_date = start_date + timedelta(days=month_range(i.get("year"), i.get("numbering")))


			if i.get("period_name") == "Year":
				start_date =  str(i.get("year")) + "-" + "01" +"-"+ "01"
				end_date =  str(i.get("year")) + "-" + "12" +"-"+ "30"
				start_date = getdate(start_date)
				end_date = getdate(end_date)

			if start_date and end_date:
				value =  frappe.db.sql(""" select  s.transaction_date, i.item_code , i.item_name , i.item_group , 
					sum(i.amount)  as value_inclusive , 
					sum(i.amount)  as value_exclusive , 
					sum(i.amount)  as return_exclusive , 
					sum(i.amount)  as return_inclusive , 
					sum(i.amount)  as sales_return , 
					YEAR(s.transaction_date) as year 
					from `tabSales Order` s
					inner join 	`tabSales Order Item` i  on s.name = i.parent		

					inner join `tabSales Team` sp on s.name = sp.parent			
					where 1=1 and s.transaction_date >= '{}' and s.transaction_date <= '{}'
					{}   group by i.item_code order by  i.item_code , s.transaction_date desc """.format( start_date  , end_date , conditions_2), as_dict=1, debug=1)
				for v in value:
					data.append(v)
	else:
		print("Normal Data - - - ")
		data  = get_data_normal(conditions = conditions )


	return columns , data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.transaction_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and s.transaction_date <=  '{}' ".format(filters.get("to_date"))

	if filters.get("item_code"):
		conditions += " and i.item_code =  '{}' ".format(filters.get("item_code"))


	if filters.get("company"):
		conditions += " and s.company =  '{}' ".format(filters.get("company"))

	if filters.get("status"):
		conditions += " and s.status =  '{}' ".format(filters.get("status"))

	return conditions


def get_conditions_2(filters):
	conditions = ""
	if filters.get("item_code"):
		conditions += " and i.item_code =  '{}' ".format(filters.get("item_code"))
	if filters.get("company"):
		conditions += " and s.company =  '{}' ".format(filters.get("company"))

	return conditions



def get_data_normal(conditions   = "", filters = ""):
		data =  frappe.db.sql(""" select  s.transaction_date, i.item_code , i.item_name , i.item_group , 
			sum(i.amount)  as value_inclusive , 
			sum(i.amount)  as value_exclusive , 
			sum(i.amount)  as return_exclusive , 
			sum(i.amount)  as return_inclusive , 
			sum(i.amount)  as sales_return , 
			YEAR(s.transaction_date) as year 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent		

			inner join `tabSales Team` sp on s.name = sp.parent			
			where 1=1 {}   group by i.item_code order by  i.item_code , s.transaction_date desc """.format(conditions ), as_dict=1, debug=1)
		return data











def get_group_range(conditions = "",  filters = {} ,   ranging_group = ""):
	if ranging_group:
		grouping = ranging_group.get("grouping")
		numbering = ranging_group.get("numbering")

		active_filter = ranging_group.get("active_filter")
		sorting = ranging_group.get("sorting")

		ranges = ranging_group.get("ranges")

		data =  frappe.db.sql(""" select 
			concat('{}', '-', {}   , '-', YEAR(s.transaction_date) ) as period , 
			{}   as numbering,
			{} as ranged,
			'{}' as period_name  , 
			YEAR(s.transaction_date) as year 			
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent	
			inner join `tabSales Team` sp on s.name = sp.parent
			where 1=1  
			{}  {}  {}  
			""".format(  ranges , numbering , 
				numbering  , numbering     , ranges , 
				conditions  , grouping ,   sorting), as_dict=1, debug=1)		

		return data




def get_data_with_range(conditions_2   = "", filters = {} , range_value = "" ,   range_year = ""):
		data =  frappe.db.sql(""" select  s.transaction_date, i.item_code , i.item_name , i.item_group , 
			sum(i.amount)  as value_inclusive , 
			sum(i.amount)  as value_exclusive , 
			sum(i.amount)  as return_exclusive , 
			sum(i.amount)  as return_inclusive , 
			sum(i.amount)  as sales_return , 
			YEAR(s.transaction_date) as year 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent		

			inner join `tabSales Team` sp on s.name = sp.parent			
			where 1=1 


			{}   group by i.item_code order by  i.item_code , s.transaction_date desc """.format(conditions_2 ), as_dict=1, debug=1)
		return data




def get_columns(conditions = "",filters = {}  ):
	columns = []


	if filters.range:

		columns.append(
		{
		"fieldname": "period",
		"label": _("Period"),
		"fieldtype": "Data",
		"width": 150
		})




	columns.append(
	{
	"fieldname": "item_code",
	"label": _("Item Code"),
	"fieldtype": "Data",
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
	"fieldtype": "Data",
	"width": 150
	})



	columns.append(
	{
	"fieldname": "qoutation_invoice",
	"label": _("Qoutation Invoice "),
	"fieldtype": "Data",
	"width": 150
	})

	columns.append(
	{
	"fieldname": "qoutation_value",
	"label": _("Qoutation Value "),
	"fieldtype": "Data",
	"width": 150
	})







	columns.append(
	{
	"fieldname": "cost",
	"label": _(" Cost "),
	"fieldtype": "Data",
	"width": 150
	})



	columns.append(
	{
	"fieldname": "exclusive",
	"label": _(" Exclusive "),
	"fieldtype": "Data",
	"width": 150
	})

	columns.append(
	{
	"fieldname": "qty",
	"label": _("Qty "),
	"fieldtype": "Data",
	"width": 150
	})





	return columns







def range_grouping(filters = None):
	active_filter = ""
	grouping = ""
	grouping_range = ""
	numbering = ""
	sorting = ""
	ranges = ""

	if filters.get("range"):
		if filters.get("range")=='Week':
			# frappe.msgprint(cstr(filters.get("range")))
			grouping += " group by  WEEK(s.transaction_date),  YEAR(s.transaction_date)"
			grouping_range += " group by  WEEK(s.transaction_date),  YEAR(s.transaction_date)"
			sorting += " order by  WEEK(s.transaction_date) asc , YEAR(s.transaction_date)"
			numbering = "WEEK(s.transaction_date)"
			ranges = "Week"

		if filters.get("range")=='Month':
			# frappe.msgprint(cstr(filters.get("range")))
			grouping +=  " group by  MONTH(s.transaction_date),  YEAR(s.transaction_date) "
			grouping_range +=  " group by  MONTH(s.transaction_date),  YEAR(s.transaction_date) "
			sorting += " order by MONTH(s.transaction_date) asc , YEAR(s.transaction_date) "
			numbering = "MONTH(s.transaction_date)"
			ranges = "Month"


		if filters.get("range")=='Year':			
			# frappe.msgprint(cstr(filters.get("range")))
			grouping +=  " group by YEAR(s.transaction_date) "
			grouping_range +=  " group by YEAR(s.transaction_date) "
			sorting += " order by YEAR(s.transaction_date) asc"
			ranges = "Year"
			numbering = "YEAR(s.transaction_date)"


		if filters.get("range")=='Quarter':
			# frappe.msgprint(cstr(filters.get("range")))
			grouping +=  " gorup by Quarter(s.transaction_date)   ,YEAR(s.transaction_date)"
			grouping_range +=  " group by Quarter(s.transaction_date) "
			sorting += " order by Quarter(s.transaction_date) asc"
			ranges = "Quarter"
			numbering = "Quarter(s.transaction_date)"

	else:
		sorting = "ORDER BY s.transaction_date asc "
		ranges = ""


	return  { "grouping" : grouping , "active_filter" : filters.get("range") , 
			"numbering" : numbering  , "sorting" : sorting  , "ranges" : ranges  , "grouping_range" : grouping_range }














@frappe.whitelist()
def month_range(year, month):
	return calendar.monthrange(year, month)[1]



def get_month_name(num):
	months_name = {1 : "Jan",2 : "Feb",3 : "Mar",4 : "Apr",5 : "May",6 : "June",7 : "July",8 : "Aug",9 : "Sept",10 : "Oct",11 : "Nov",12 : "Dec"}
	return months_name.get(num)
@frappe.whitelist()
def monday_of_calenderweek(year = 2020,week = 1):
    year = int(year)
    week = int(week)
    first = date(year, 1, 1)

    base = 1 if first.isocalendar()[1] == 1 else 8
    return first + timedelta(days=base - first.isocalendar()[2] + 7 * (week - 1))

