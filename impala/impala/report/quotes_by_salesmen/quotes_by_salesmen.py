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
	data = []
	new_column = []
	map_group = {}



	ranging_group = range_grouping(filters) 

	values_query = get_values_column(conditions = conditions , filters = filters)


	if filters.get("range"):
		ranging_group = range_grouping(filters)
		level_1 = group_level_1(conditions = conditions , filters = filters)
		# frappe.msgprint("Level 1 and level 2 and level 3 ")
		for i in level_1:
			# data.append({"sales_person" : i.get("sales_person") })
			range_level_1 = get_data_with_level_1_wtih_range(conditions = conditions ,  
				grouping_level_value_1 = i.get("sales_person") ,  ranging_group = ranging_group  ,  values_query = values_query)
			
			if range_level_1:
				level_1_row = {}
				main_group = frappe.scrub(i.get("sales_person")) # customer -- Waliullah  map_group = {}
				for b in range_level_1:
					row = {}
					mrow  ={}
					child_group = b.get("period")
					if main_group in map_group:
						print("main Group --- ")
						if child_group in main_group:
							value_exist = main_group.get(b.get("period"))
							value_exist =+ b.value
							map_group[main_group].update({ b.get("period") :  value_exist }) 

							mrow[child_group ] = b.value
							mrow[main_group] = i.get("sales_person")

							print("")
						else:
							print("add Child ")
							map_group[main_group][b.get("period")] = b.value 
							mrow[child_group ] = b.value
							mrow[main_group] = i.get("sales_person")
					else:
						print("Main Group not Found. ")
						map_group[main_group] = {child_group :  b.value } 
						mrow[child_group ] = b.value
						mrow[main_group] = i.get("sales_person")
					row = {
					main_group  : main_group  , 
					b.get("period")  : b.get("period") , 
					"qty" : b.get("value") or "",	
					"value" : b.get("value") or "",
					}

				level_1_row = map_group.get(main_group)
				level_1_row["sales_person"]  =  i.get("sales_person") 
				data.append(level_1_row)



		new_col = get_range_group_for_columns(conditions = conditions , filters = filters)

		# frappe.msgprint(cstr(new_col))


		if new_col:
			columns = get_columns(conditions = conditions , filters = filters ,  get_range_group_for_columns = new_col)
		else:
			columns = get_columns(conditions , filters)



	else:
		print("Normal Data - - - ")
		columns = get_columns(conditions , filters)
		data  = get_data_normal(conditions = conditions )


	# frappe.msgprint(cstr(map_group))
	# frappe.msgprint(cstr(columns))
	# frappe.msgprint(cstr(data))

	return columns , data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.transaction_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and s.transaction_date <=  '{}' ".format(filters.get("to_date"))

	if filters.get("sales_person"):
		conditions += " and sp.sales_person =  '{}' ".format(filters.get("sales_person"))


	if filters.get("company"):
		conditions += " and s.company =  '{}' ".format(filters.get("company"))

	return conditions




def group_level_1(conditions   = "", filters = ""):
		data =  frappe.db.sql(""" select  s.transaction_date, sp.sales_person 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent		

			inner join `tabSales Team` sp on s.name = sp.parent			
			where 1=1 {}   group by sp.sales_person order by  sp.sales_person , s.transaction_date desc """.format(conditions ), as_dict=1, debug=1)
		return data




# when level 2 filres is not active data will be fetch base on level group. as inner records. 
def group_level_1_1(conditions = "" , grouping_level_1 = None,  grouping_level_value  = None, range_by = None , filters = None):
	if grouping_level_1:
		grouping = grouping_level_1.get("grouping")
		numbering = grouping_level_1.get("numbering")
		data =  frappe.db.sql(""" select  {} as level_1,  s.transaction_date, s.name  as voucher_no , i.item_code , i.qty , 

			(i.amount *  i.total_tax_percentage  / 100)  as amount_exclusive , 
			s.tax_type ,  i.total_tax_percentage ,

			sum(i.amount)  as value_inclusive , 
			sum(i.amount)  as value_exclusive , 
			sum(i.amount)  as return_exclusive , 
			sum(i.amount)  as return_inclusive , 
			sum(i.amount)  as sales_return , 




			i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
			i.amount as gp,  s.territory , s.customer , s.project ,  s.cost_center as division ,
			YEAR(s.transaction_date) as year 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent		
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and {} = '{}' {}   order by s.transaction_date desc """.format(numbering , numbering , grouping_level_value , conditions  ), as_dict=1, debug=1)
	return data




def get_data_normal(conditions   = "", filters = ""):
		data =  frappe.db.sql(""" select  s.transaction_date, sp.sales_person ,
			sum(i.amount)  as value_inclusive , 
			sum(i.amount)  as value_exclusive , 
			sum(i.amount)  as return_exclusive , 
			sum(i.amount)  as return_inclusive , 
			sum(i.amount)  as sales_return , 
			YEAR(s.transaction_date) as year 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent		

			inner join `tabSales Team` sp on s.name = sp.parent			
			where 1=1 {}   group by sp.sales_person order by  sp.sales_person , s.transaction_date desc """.format(conditions ), as_dict=1, debug=1)
		return data



def get_data_with_level_1_2(conditions   = "", filters = "" , level_1 = "" , level_2 = ""):
		data =  frappe.db.sql(""" select  sum(i.qty) as qty , 
			YEAR(s.transaction_date) as year 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent		
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and s.customer = '{}' and i.item_code = '{}' {}  order by s.transaction_date desc """.format( level_1 , level_2 , conditions), as_dict=1, debug=1)									
		return data












def get_data_with_level_1_wtih_range(conditions = "",   grouping_level_value_1 = "" ,  ranging_group = ""  , values_query = "" ):
	if ranging_group:
		grouping = ranging_group.get("grouping")
		numbering = ranging_group.get("numbering")

		active_filter = ranging_group.get("active_filter")
		sorting = ranging_group.get("sorting")

		ranges = ranging_group.get("ranges")

		data =  frappe.db.sql(""" select  sp.sales_person , 
			concat('{}', '-', {}   , '-', YEAR(s.transaction_date) ) as period , 
			{}   as numbering,
			{} as ranged,
			YEAR(s.transaction_date) as year ,
			
			sum(i.qty) as qty 
			{}
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent	
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and   sp.sales_person  = '{}' 
			{}  {}  {}  
			""".format(  ranges , numbering , 
				numbering  , numbering   , values_query   ,  grouping_level_value_1 , 
				conditions  , grouping ,   sorting), as_dict=1, debug=1)		

		return data





def get_columns(conditions = "",filters = {} , get_range_group_for_columns = "" ):
	columns = []
	columns.append(
	{
	"fieldname": "sales_person",
	"label": _("Sales Person"),
	"fieldtype": "Data",
	"width": 150
	})


	if not filters.range:
		columns.append(
		{
		"fieldname": "value_inclusive",
		"label": _("Sales Value Inlusive"),
		"options" : "Currency",
		"width": 150
		})


		columns.append(
		{
		"fieldname": "value_exclusive",
		"label": _("Sales Value Exlusive"),
		"options" : "Currency",
		"width": 150
		})



		columns.append(
		{
		"fieldname": "return_inclusive",
		"label": _("Return Value Inlusive"),
		"options" : "Currency",
		"width": 150
		})


		columns.append(
		{
		"fieldname": "return_exclusive",
		"label": _("Return Value Exlusive"),
		"options" : "Currency",
		"width": 150
		})


		columns.append(
		{
		"fieldname": "sales_return",
		"label": _("Sales Return "),
		"fieldtype": "Data",
		"width": 150
		})




	if filters.range:

		if filters.range == "Month":
			if get_range_group_for_columns:
				for i in get_range_group_for_columns:
					month_name = get_month_name(i.get("numbering"))
					columns.append(
						{
						"fieldname": i.period,
						"label": month_name+"-"+str(i.get("year")),
						"fieldtype": "Data",
						"width": 160
						})
		elif filters.range == "Week":
			if get_range_group_for_columns:
				for i in get_range_group_for_columns:
					columns.append(
					{
					"fieldname": i.period,
					"label": i.period,
					"fieldtype": "Data",
					"width": 140
					})



		elif filters.range == "Year":
			if get_range_group_for_columns:
				for i in get_range_group_for_columns:
					columns.append(
						{
						"fieldname":i.period ,
						"label": str(i.get("year")) ,
						"fieldtype": "Data",
						"width": 140
						})

		elif filters.range == "Quarter":
			if get_range_group_for_columns:
				for i in get_range_group_for_columns:
					columns.append(
						{
						"fieldname":i.period ,
						"label": i.period ,
						"fieldtype": "Data",
						"width": 140
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
			grouping += " group by  WEEK(s.transaction_date),  YEAR(s.transaction_date)"
			grouping_range += " group by  WEEK(s.transaction_date),  YEAR(s.transaction_date)"
			sorting += " order by  WEEK(s.transaction_date) asc , YEAR(s.transaction_date)"
			numbering = "WEEK(s.transaction_date)"
			ranges = "Week"

		if filters.get("range")=='Month':
			grouping +=  " group by  MONTH(s.transaction_date),  YEAR(s.transaction_date) "
			grouping_range +=  " group by  MONTH(s.transaction_date),  YEAR(s.transaction_date) "
			sorting += " order by MONTH(s.transaction_date) asc , YEAR(s.transaction_date) "
			numbering = "MONTH(s.transaction_date)"
			ranges = "Month"


		if filters.get("range")=='Year':
			grouping +=  " group by YEAR(s.transaction_date) "
			grouping_range +=  " group by YEAR(s.transaction_date) "
			sorting += " order by YEAR(s.transaction_date) asc"
			ranges = "Year"
			numbering = "YEAR(s.transaction_date)"


		if filters.get("range")=='Quarter':
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








def get_values_column( conditions = ""  , filters = ""):
	values = ""
	if filters.get("value") and filters.get("value") != "":
		if filters.get("value") == "Qty":
			values+= " , sum(i.qty) as value "
			# frappe.msgprint("Qty is Selected Filters".format(values))
		if filters.get("value") == "Value Exclusive":
			values+= " , sum((i.amount *  i.total_tax_percentage  / 100))   as value "
		if filters.get("value") == "Value Inclusive":
			values+= " , sum(i.amount) as value "

		if filters.get("value") == "Return Exclusive":
			values+= " , sum(i.amount) as value "

		if filters.get("value") == "Sales Return":
			values+= " , sum(i.amount) as value "
	else:
		values+= " , sum(i.qty) as value"
	return values






def get_range_group_for_columns(conditions = "", filters  = ""):
	query_string_level = ""

	query_string_group = ""

	query_string_sorting = ""

	query_string_range = ""


	query_string_level += " sp.sales_person  "

	if filters.range and filters.range != "":
		grouping_ranged = range_grouping(filters)
		grouping_range = ""
		sorting = ""
		numbering_range = ""
		ranges = ""

		if grouping_ranged:
			grouping_range = grouping_ranged.get("grouping_range")
			numbering_range = grouping_ranged.get("numbering") # s.customer 
			ranges = grouping_ranged.get("ranges") # s.customer 

			query_string_range +=  """ ,
						concat('{}', '-', {}   , '-', YEAR(s.transaction_date) ) as period , 
						{}   as numbering,
						{} as ranged,
						YEAR(s.transaction_date) as year """.format(ranges , numbering_range ,  numbering_range  , numbering_range )

			data =  frappe.db.sql(""" select  DISTINCT  s.transaction_date {}  
				from `tabSales Order` s
				inner join 	`tabSales Order Item` i  on s.name = i.parent	
				inner join `tabSales Team` sp on s.name = sp.parent
				where 1=1  {}  {} order by s.transaction_date   """.format( query_string_range ,   conditions  , grouping_range   ), as_dict=1, debug=1)		

			return data








@frappe.whitelist()
def month_range(year, month):
	return calendar.monthrange(year, month)[1]



def get_month_name(num):
	months_name = {1 : "Jan",2 : "Feb",3 : "Mar",4 : "Apr",5 : "May",6 : "June",7 : "July",8 : "Aug",9 : "Sept",10 : "Oct",11 : "Nov",12 : "Dec"}
	return months_name.get(num)
