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
	data = []
	new_column = []
	map_group = {}



	if filters.get("level_1") and filters.get("level_1") != "":

		grouping_level_1 = grouping_by_level_1(filters) 

 

		ranging_group = range_grouping(filters) 

		values_query = get_values_column(conditions = conditions , filters = filters)







		# frappe.msgprint(cstr(grouping_level_1))
		level_1 = group_level_1(conditions = conditions , grouping_level_1 = grouping_level_1 , filters = filters)
		# frappe.msgprint(cstr(level_1))

		if level_1:
			if  not filters.get("value") and not filters.get("range"):
				for i in level_1:
					data.append({"level_1" : i.get("level_1")})
					level_1_child = group_level_1_1(conditions = conditions , grouping_level_1 = grouping_level_1,  grouping_level_value  = i.get("level_1"))
					for b in level_1_child:
						row = {
						"period" : b.get("period") or "",
						"ranging" : b.get("ranging") or "",
						"ranges" : b.get("ranges") or "",
						"year" : b.get("year") or "",

						"item_code" : b.get("item_code") or "",
						"item_name" : b.get("item_name") or "",
						"item_group" : b.get("item_group") or "",

						"qty" : b.get("qty") or "",	
						"amount_exclusive" : b.get("amount_exclusive") or "",
						"item_cost" : b.get("item_cost") or "",

						"value" : b.get("value") or "",
						}
						data.append(row)

		


			
			elif filters.get("level_1")  and  filters.get("range"):
				ranging_group = range_grouping(filters)

				# frappe.msgprint("Level 1 and level 2 and level 3 ")
				for i in level_1:
					# data.append({"level_1" : i.get("level_1") })
					range_level_1 = get_data_with_level_1_wtih_range(conditions = conditions , grouping_level_1 = grouping_level_1 , 
						grouping_level_value_1 = i.get("level_1") ,  ranging_group = ranging_group  ,  values_query = values_query)
					
					if range_level_1:
						level_1_row = {}
						main_group = frappe.scrub(i.get("level_1")) # customer -- Waliullah  map_group = {}
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
									mrow[main_group] = i.get("level_1")

									print("")
								else:
									print("add Child ")
									map_group[main_group][b.get("period")] = b.value 
									mrow[child_group ] = b.value
									mrow[main_group] = i.get("level_1")
							else:
								print("Main Group not Found. ")
								map_group[main_group] = {child_group :  b.value } 
								mrow[child_group ] = b.value
								mrow[main_group] = i.get("level_1")
							row = {
							main_group  : main_group  , 
							b.get("period")  : b.get("period") , 
							"qty" : b.get("value") or "",	
							"value" : b.get("value") or "",
							}

						level_1_row = map_group.get(main_group)
						level_1_row["level_1"]  =  i.get("level_1") 
						data.append(level_1_row)





		new_col = get_range_group_for_columns(conditions = conditions , filters = filters)
		if new_col:
			columns = get_columns(conditions = conditions , filters = filters ,  get_range_group_for_columns = new_col)
		else:
			columns = get_columns(conditions = conditions , filters = filters)



	else:
		print("Normal Data - - - ")
		columns = get_columns(conditions  = conditions, filters = filters)
		data  = get_data_normal(conditions = conditions )


	# frappe.msgprint(cstr(map_group))
	# frappe.msgprint(cstr(columns))
	# frappe.msgprint(cstr(data))

	return columns , data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.posting_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and s.posting_date <=  '{}' ".format(filters.get("to_date"))
	return conditions



def group_level_1(conditions = "" , grouping_level_1 = None, range_by = None , filters = None):
	data = []
	if grouping_level_1:
		grouping = grouping_level_1.get("grouping")
		numbering = grouping_level_1.get("numbering")

		data =  frappe.db.sql(""" select {}  as level_1 , 
			YEAR(s.posting_date) as year 
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent
			inner join `tabSales Team` sp on s.name = sp.parent
			where 1=1 {}   {}  order by s.posting_date desc """.format( numbering ,  conditions , grouping), as_dict=1, debug=1)									
	return data

# when level 2 filres is not active data will be fetch base on level group. as inner records. 
def group_level_1_1(conditions = "" , grouping_level_1 = None,  grouping_level_value  = None, range_by = None , filters = None):
	if grouping_level_1:
		grouping = grouping_level_1.get("grouping")
		numbering = grouping_level_1.get("numbering")
		data =  frappe.db.sql(""" select  {} as level_1, 


		i.item_code  ,  i.item_name , i.item_group , 

		i.amount as item_cost , 

		sum(i.qty) as qty , 

		IF( s.tax_type= 'Exclusive' , 
			sum((i.amount *  i.total_tax_percentage  / 100) + i.amount)  , 
			sum(i.amount) 
		) as amount_exclusive  


		from `tabSales Invoice` s
		inner join 	`tabSales Invoice Item` i  on s.name = i.parent		
		inner join `tabSales Team` sp on s.name = sp.parent


		where 1=1  and {} = '{}' {}   order by s.posting_date desc 
		""".format(numbering , numbering , grouping_level_value , conditions  ), as_dict=1, debug=1)
	return data







def get_data_normal(conditions   = "", filters = ""):




	


	data =  frappe.db.sql(""" select  


		i.item_code  ,  i.item_name , i.item_group , 

		sum(i.qty) as qty , 

		IF( s.tax_type= 'Exclusive' , 
			sum((i.amount *  i.total_tax_percentage  / 100) + i.amount)  , 
			sum(i.amount) 
		) as amount_exclusive  







		from `tabSales Invoice` s
		inner join 	`tabSales Invoice Item` i  on s.name = i.parent		
		inner join `tabSales Team` sp on s.name = sp.parent
		where 1=1  
		order by s.posting_date
		
		   """  , as_dict = 1 ) 	
	return data

















def get_data_with_level_1_2(conditions   = "", filters = "" , level_1 = "" , level_2 = ""):
		data =  frappe.db.sql(""" select  sum(i.qty) as qty , 
			YEAR(s.posting_date) as year 
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent		
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and s.customer = '{}' and i.item_code = '{}' {}  order by s.posting_date desc """.format( level_1 , level_2 , conditions), as_dict=1, debug=1)									
		return data












def get_data_with_level_1_wtih_range(conditions = "", grouping_level_1 = "" , grouping_level_value_1 = "" ,   ranging_group = ""  , values_query = "" ):
	if grouping_level_1:
		grouping_1 = grouping_level_1.get("grouping")
		numbering_1 = grouping_level_1.get("numbering")

		if ranging_group:
			grouping = ranging_group.get("grouping")
			numbering = ranging_group.get("numbering")

			active_filter = ranging_group.get("active_filter")
			sorting = ranging_group.get("sorting")

			ranges = ranging_group.get("ranges")






		data =  frappe.db.sql(""" select  {}   as level_1 , 
			concat('{}', '-', {}   , '-', YEAR(s.posting_date) ) as period , 
			{}   as numbering,
			{} as ranged,
			YEAR(s.posting_date) as year ,
			
			sum(i.qty) as qty 
			{}
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent	
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and   {}  = '{}' {} {}  {}
			order by {}  asc,   s.posting_date asc ,  {} asc , YEAR(s.posting_date) asc """.format( numbering_1 , ranges , numbering , 
				numbering  , numbering   , values_query , numbering_1  ,  grouping_level_value_1 , conditions , grouping_1 , grouping , numbering_1 , numbering), as_dict=1, debug=1)		

		return data





def get_columns(conditions = "" ,filters = {} , get_range_group_for_columns = "" ):
	columns = []
	if filters.level_1:
		columns.append(
		{
		"fieldname": "level_1",
		"label": filters.level_1,
		"fieldtype": "Data",
		"width": 100
		})


	if filters.level_2:

		columns.append(
		{
		"fieldname": "level_2",
		"label": filters.level_2,
		"fieldtype": "Data",
		"width": 100
		})


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











	if filters.range == "" or not filters.range:

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
		"options" : "Item Group",
		"width": 150
		})


		columns.append(
		{
		"fieldname": "item_cost",
		"label": _("Item Cost"),
		"options" : "Float",
		"width": 150
		})



		columns.append(
		{
		"fieldname": "qty",
		"label": _("Qty"),
		"options" : "Data",
		"width": 150
		})


		columns.append(
		{
		"fieldname": "amount_exclusive",
		"label": _("Amount Exclusive"),
		"options" : "Data",
		"width": 150
		})






	return columns






def grouping_by_level_1(filters):


	grouping = ""
	sorting = ""
	numbering = ""
	if filters.get("level_1") and filters.get("level_1") != "":
		if filters.get("level_1")=='Customer':
			grouping += "group by s.customer"
			numbering = "s.customer"


		if filters.get("level_1")=='Item Group':
			grouping += "group by i.item_group"
			numbering = "i.item_group"


		if filters.get("level_1")=='Item':
			grouping += "group by i.item_code  "
			numbering = "i.item_code"



		if filters.get("level_1")=='Territory':
			grouping += "group by s.territory "
			numbering = "s.territory"


		if filters.get("level_1")=='Sales Person':
			grouping += "group by sp.sales_person  "
			numbering = "sp.sales_person"

		if filters.get("level_1")=='Division':
			grouping += "group by s.cost_center  "
			numbering = "s.cost_center"

	return { "grouping" : grouping , "numbering" : numbering }







def range_grouping(filters = None):
	active_filter = ""
	grouping = ""
	grouping_range = ""
	numbering = ""
	sorting = ""
	ranges = ""

	if filters.get("range"):
		if filters.get("range")=='Week':
			grouping += ",WEEK(s.posting_date),  YEAR(s.posting_date)"
			grouping_range += " group by  WEEK(s.posting_date),  YEAR(s.posting_date)"
			sorting += ",WEEK(s.posting_date) asc"
			numbering = "WEEK(s.posting_date)"
			ranges = "Week"

		if filters.get("range")=='Month':
			grouping +=  ",MONTH(s.posting_date),  YEAR(s.posting_date) "
			grouping_range +=  " group by  MONTH(s.posting_date),  YEAR(s.posting_date) "
			sorting += ",MONTH(s.posting_date) asc , YEAR(s.posting_date) "
			numbering = "MONTH(s.posting_date)"
			ranges = "Month"


		if filters.get("range")=='Year':
			grouping +=  ",YEAR(s.posting_date) "
			grouping_range +=  " group by YEAR(s.posting_date) "
			sorting += ",YEAR(s.posting_date) asc"
			ranges = "Year"
			numbering = "YEAR(s.posting_date)"


		if filters.get("range")=='Quarter':
			grouping +=  ",Quarter(s.posting_date) "
			grouping_range +=  " group by Quarter(s.posting_date) "
			sorting += ",Quarter(s.posting_date) asc"
			ranges = "Quarter"
			numbering = "Quarter(s.posting_date)"

	else:
		sorting = "ORDER BY s.posting_date asc "
		ranges = ""


	return  { "grouping" : grouping , "active_filter" : filters.get("range") , 
			"numbering" : numbering  , "sorting" : sorting  , "ranges" : ranges  , "grouping_range" : grouping_range }








def get_values_column( conditions = ""  , filters = ""):





	values = ""
	if filters.get("value") and filters.get("value") != "":
		if filters.get("value") == "Qty":
			values+= " , sum(i.qty) as value "
			# frappe.msgprint("Qty is Selected Filters".format(values))
		if filters.get("value") == "sale_exclusive":
			values+= """ , 
				IF( s.tax_type= 'Exclusive' , 
					(i.amount *  i.total_tax_percentage  / 100) + i.amount  , 
					i.amount 
				) as value  """

		if filters.get("value") == "Amount Enclusive":
			values+= """  , 
				IF( s.tax_type= 'Inclusive' , 
					i.amount -  (i.amount *  i.total_tax_percentage  / 100)   , 
					0
				) as value   
			"""


	else:

		values+= """ , 
			IF( s.tax_type= 'Exclusive' , 
				(i.amount *  i.total_tax_percentage  / 100) + i.amount  , 
				i.amount 
			) as value  """



	return values




		









def get_range_group_for_columns(conditions = "", filters  = ""):
	query_string_level = ""

	query_string_group = ""

	query_string_sorting = ""

	query_string_range = ""



	if filters.level_1 and filters.level_1 != "":

		grouping_level_1 = grouping_by_level_1(filters)

		if grouping_level_1:
			grouping_1 = grouping_level_1.get("grouping")
			numbering_1 = grouping_level_1.get("numbering") # s.customer 

			query_string_level += " {} as level_1 ".format(numbering_1)


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
							concat('{}', '-', {}   , '-', YEAR(s.posting_date) ) as period , 
							{}   as numbering,
							{} as ranged,
							YEAR(s.posting_date) as year """.format(ranges , numbering_range ,  numbering_range  , numbering_range )

				data =  frappe.db.sql(""" select  DISTINCT  s.name ,  {}  {}  
					from `tabSales Invoice` s
					inner join 	`tabSales Invoice Item` i  on s.name = i.parent	
					inner join `tabSales Team` sp on s.name = sp.parent
					where 1=1  {}  {} order by s.name   """.format( query_string_level , query_string_range ,   conditions  , grouping_range   ), as_dict=1, debug=1)		

				return data








@frappe.whitelist()
def month_range(year, month):
	return calendar.monthrange(year, month)[1]



def get_month_name(num):
	months_name = {1 : "Jan",2 : "Feb",3 : "Mar",4 : "Apr",5 : "May",6 : "June",7 : "July",8 : "Aug",9 : "Sept",10 : "Oct",11 : "Nov",12 : "Dec"}
	return months_name.get(num)
