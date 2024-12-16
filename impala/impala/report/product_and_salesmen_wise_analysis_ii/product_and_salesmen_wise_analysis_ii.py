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

	columns = get_columns(conditions  = conditions, filters = filters)


	if filters.get("level_1") and filters.get("level_1") != "":

		grouping_level_1 = grouping_by_level_1(filters) 

		grouping_level_2 = grouping_by_level_2(filters) 
 

		ranging_group = range_grouping(filters) 

		values_query =  ""







		# frappe.msgprint(cstr(grouping_level_1))
		level_1 = group_level_1(conditions = conditions , grouping_level_1 = grouping_level_1 , filters = filters)
		# frappe.msgprint(cstr(level_1))

		if level_1:
			if not filters.get("level_2")   and not filters.get("range"):
				for i in level_1:
					data.append({"level_1" : i.get("level_1")})
					level_1_child = group_level_1_1(conditions = conditions , grouping_level_1 = grouping_level_1,  grouping_level_value  = i.get("level_1"))
					for b in level_1_child:
						row = {
						"period" : b.get("period") or "",
						"ranging" : b.get("ranging") or "",
						"ranges" : b.get("ranges") or "",
						"year" : b.get("year") or "",

						"division" : b.get("division") or "",
						"territory" : b.get("territory") or "",
						"sales_person" : b.get("sales_person") or "",	
						"customer" : b.get("customer") or "",


						"return_amount_inclusive" : b.get("return_amount_inclusive") or "",
						"return_amount_exclusive" : b.get("return_amount_exclusive") or "",
						"sales_amount_exclusive" : b.get("sales_amount_exclusive") or "",	
						"sales_amount_inclusive" : b.get("sales_amount_inclusive") or "",

						"sales_to_inclusive" : b.get("sales_to_inclusive") or "",




						"item_code" : b.get("item_code") or "",
						"item_name" : b.get("item_name") or "",
						"item_group" : b.get("item_group") or "",


						"transaction_date" : b.get("transaction_date") or "",
						"voucher_no" : b.get("voucher_no") or "",
						"qty" : b.get("qty") or "",	
						"amount_exclusive" : b.get("amount_exclusive") or "",
						"item_cost" : b.get("item_cost") or "",
						"amount_inclusive" : b.get("amount_inclusive") or "",
						"gross_profit" : b.get("gross_profit") or "",
						"gp" : b.get("gp") or "",
						"value" : b.get("value") or "",
						}
						data.append(row)

			elif filters.get("level_1") and  filters.get("level_2")  and not filters.get("range"):
				# frappe.msgprint("Level 1 and level 2 ")
				print("")


				for i in level_1:
					data.append({"level_1" : i.get("level_1")})
					level_2  = group_level_2(conditions = "" , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , grouping_level_2 = grouping_level_2)
					for b in level_2:
						data.append({"level_2" : b.get("level_2")})
						level_2_child = group_level_2_2(conditions = conditions , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , 
							grouping_level_2  = grouping_level_2 , grouping_level_value_2 = b.get("level_2") )
						for c in level_2_child:
							row = {
							"period" : c.get("period") or "",
							"ranging" : c.get("ranging") or "",
							"ranges" : c.get("ranges") or "",
							"year" : c.get("year") or "",

							"division" : c.get("division") or "",
							"territory" : c.get("territory") or "",
							"sales_person" : c.get("sales_person") or "",	
							"customer" : c.get("customer") or "",

							"item_code" : c.get("item_code") or "",
							"item_name" : b.get("item_name") or "",


							"return_amount_inclusive" : c.get("return_amount_inclusive") or "",
							"return_amount_exclusive" : c.get("return_amount_exclusive") or "",
							"sales_amount_exclusive" : c.get("sales_amount_exclusive") or "",	
							"sales_amount_inclusive" : c.get("sales_amount_inclusive") or "",

							"sales_to_inclusive" : c.get("sales_to_inclusive") or "",









							"item_group" : c.get("item_group") or "",

							"voucher_no" : b.get("voucher_no") or "",



							"transaction_date" : c.get("transaction_date") or "",
							"qty" : c.get("qty") or "",	
							"amount_exclusive" : c.get("amount_exclusive") or "",
							"item_cost" : c.get("item_cost") or "",
							"amount_inclusive" : c.get("amount_inclusive") or "",
							"gross_profit" : c.get("gross_profit") or "",
							"gp" : c.get("gp") or "",
							"value" : c.get("value") or "",
							}
							data.append(row)






			
			elif filters.get("level_1")  and  filters.get("range") and not filters.get("level_2") :
				ranging_group = range_grouping(filters)

				# frappe.msgprint("Level 1 and level 2 and level 3 ")
				for i in level_1:
					data.append({"level_1" : i.get("level_1") })

					range_level_1 = get_data_with_level_1_wtih_range(conditions = conditions , grouping_level_1 = grouping_level_1 , 
						grouping_level_value_1 = i.get("level_1") ,  ranging_group = ranging_group  ,  values_query = values_query)
					if range_level_1:
						print()
						for c in range_level_1:
							row = {
							"period" : c.get("period") or "",
							"ranging" : c.get("ranging") or "",
							"ranges" : c.get("ranges") or "",
							"year" : c.get("year") or "",
							"division" : c.get("division") or "",
							"territory" : c.get("territory") or "",
							"sales_person" : c.get("sales_person") or "",	
							"customer" : c.get("customer") or "",
							"item_code" : c.get("item_code") or "",
							"item_name" : c.get("item_name") or "",
							"item_group" : c.get("item_group") or "",
							"voucher_no" : c.get("voucher_no") or "",





							"return_amount_inclusive" : c.get("return_amount_inclusive") or "",
							"return_amount_exclusive" : c.get("return_amount_exclusive") or "",
							"sales_amount_exclusive" : c.get("sales_amount_exclusive") or "",	
							"sales_amount_inclusive" : c.get("sales_amount_inclusive") or "",

							"sales_to_inclusive" : c.get("sales_to_inclusive") or "",








							"transaction_date" : c.get("transaction_date") or "",
							"qty" : c.get("qty") or "",	
							"amount_exclusive" : c.get("amount_exclusive") or "",
							"item_cost" : c.get("item_cost") or "",
							"amount_inclusive" : c.get("amount_inclusive") or "",
							"gross_profit" : c.get("gross_profit") or "",
							"gp" : c.get("gp") or "",
							"value" : c.get("value") or "",
							}
							data.append(row)



			elif filters.get("level_1")  and  filters.get("level_2")  and  filters.get("range"):
				ranging_group = range_grouping(filters)

				# frappe.msgprint("Level 1 and level 2 and level 3 ")
				for i in level_1:
					data.append({"level_1" : i.get("level_1") })


					level_2  = group_level_2(conditions = "" , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , grouping_level_2 = grouping_level_2)
					for b in level_2:

						data.append({"level_2" : b.get("level_2")})
						main_group_level_2 = frappe.scrub(b.get("level_2")) # customer -- Waliullah  map_group = {}
						range_level_1 = get_data_with_level_1_2_wtih_range(conditions = conditions , grouping_level_1 = grouping_level_1 , grouping_level_value_1 = i.get("level_1") , 
							grouping_level_2 = grouping_level_2 , grouping_level_value_2 = b.get("level_2") ,   ranging_group = ranging_group  )



						for c in range_level_1:
							
							row = {
							"period" :c.get("period") or "",
							"ranging" : c.get("ranging") or "",
							"ranges" : c.get("ranges") or "",
							"year" : c.get("year") or "",

							"division" : c.get("division") or "",
							"territory" : c.get("territory") or "",
							"sales_person" : c.get("sales_person") or "",	
							"customer" : c.get("customer") or "",

							"item_code" : c.get("item_code") or "",
							"item_name" : c.get("item_name") or "",

							"return_amount_inclusive" : c.get("return_amount_inclusive") or "",
							"return_amount_exclusive" : c.get("return_amount_exclusive") or "",
							"sales_amount_exclusive" : c.get("sales_amount_exclusive") or "",	
							"sales_amount_inclusive" : c.get("sales_amount_inclusive") or "",

							"sales_to_inclusive" : c.get("sales_to_inclusive") or "",
							"tax_type" : c.get("tax_type"),
							"total_tax_percentage" : c.get("total_tax_percentage") , 
							"amount" : c.get("amount") , 




							"item_group" : c.get("item_group") or "",


							"transaction_date" : c.get("transaction_date") or "",
							"qty" : c.get("qty") or "",	
							"amount_exclusive" : c.get("amount_exclusive") or "",
							"item_cost" : c.get("item_cost") or "",
							"amount_inclusive" : c.get("amount_inclusive") or "",
							"gross_profit" : c.get("gross_profit") or "",
							"gp" : c.get("gp") or "",
							"value" : c.get("value") or "",
							}
							data.append(row)




	else:
		print("Normal Data - - - ")
		data  = get_data_normal(conditions = conditions )


	# frappe.msgprint(cstr(data))

	return columns , data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.posting_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and s.posting_date <=  '{}' ".format(filters.get("to_date"))

	if filters.get("item_code"):
		conditions += " and i.item_code =  '{}' ".format(filters.get("to_date"))
	if filters.get("item_group"):
		conditions += " and i.item_group =  '{}' ".format(filters.get("item_group"))

	if filters.get("company"):
		conditions += " and s.company =  '{}' ".format(filters.get("company"))


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
		s.name as voucher_no , s.posting_date as transaction_date , 
		i.qty , 

		IF( s.tax_type= 'Exclusive' , 
			(i.amount *  i.total_tax_percentage  / 100) + i.amount  , 
			i.amount 
		) as sales_amount_exclusive  , 

		IF( s.tax_type= 'Inclusive' , 
			i.amount -  (i.amount *  i.total_tax_percentage  / 100)   , 
			0
		) as sales_amount_inclusive  , 

		IF( s.tax_type= 'Inclusive' , 
			i.amount -  (i.amount *  i.total_tax_percentage  / 100)   , 
			0
		) as return_amount_inclusive  , 

		IF( s.tax_type= 'Exclusive' , 
			 (i.amount *  i.total_tax_percentage  / 100) + i.amount  , 
			i.amount
		) as return_amount_exclusive  , 






			YEAR(s.posting_date) as year 
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent		
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and {} = '{}' {}   order by s.posting_date desc """.format(numbering , numbering , grouping_level_value , conditions  ), as_dict=1, debug=1)
	return data



def group_level_2(conditions = "" , grouping_level_1  = "", grouping_level_value_1 = "" , grouping_level_2  = ""):


	if grouping_level_1:
		grouping_1 = grouping_level_1.get("grouping")
		numbering_1 = grouping_level_1.get("numbering")


		if grouping_level_2:
			grouping_2 = grouping_level_2.get("grouping")
			numbering_2 = grouping_level_2.get("numbering")

			data =  frappe.db.sql(""" select  {} as level_1 ,  {} as level_2  ,
			YEAR(s.posting_date) as year 
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and {} = '{}' {}  {} , {} order by s.posting_date desc 
			""".format(numbering_1 , numbering_2 , numbering_1	 , grouping_level_value_1 , conditions , grouping_1  , grouping_2  ), as_dict=1, debug=1)									
			return data



def group_level_2_2(conditions = "" , grouping_level_1  = "", grouping_level_value_1 = "" , grouping_level_2  = "" , grouping_level_value_2 = ""):
	if grouping_level_1:
		grouping_1 = grouping_level_1.get("grouping")
		numbering_1 = grouping_level_1.get("numbering")

		if grouping_level_2:
			grouping_2 = grouping_level_2.get("grouping")
			numbering_2 = grouping_level_2.get("numbering")

			data =  frappe.db.sql(""" select  {} as level_1 ,  {} as level_2  ,
			


			i.item_code  ,  i.item_name , i.item_group , 
			s.name as voucher_no , s.posting_date as transaction_date , 
			i.qty , 

			IF( s.tax_type= 'Exclusive' , 
				(i.amount *  i.total_tax_percentage  / 100) + i.amount  , 
				i.amount 
			) as sales_amount_exclusive  , 

			IF( s.tax_type= 'Inclusive' , 
				i.amount -  (i.amount *  i.total_tax_percentage  / 100)   , 
				0
			) as sales_amount_inclusive  , 

			IF( s.tax_type= 'Inclusive' , 
				i.amount -  (i.amount *  i.total_tax_percentage  / 100)   , 
				0
			) as return_amount_inclusive  , 

			IF( s.tax_type= 'Exclusive' , 
				 (i.amount *  i.total_tax_percentage  / 100) + i.amount  , 
				i.amount
			) as return_amount_exclusive 














			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and {} = '{}' and  {} = '{}'  {}   order by s.posting_date desc 
			""".format(numbering_1 , numbering_2 , numbering_1	 , grouping_level_value_1 , numbering_2  , grouping_level_value_2 , conditions  ), as_dict=1, debug=1)									
			return data










def get_data_normal(conditions   = "", filters = ""):
		data =  frappe.db.sql(""" select  sp.sales_person ,  

		i.item_code  ,  i.item_name , i.item_group , 
		s.name as voucher_no , s.posting_date as transaction_date , 
		i.qty , 

		IF( s.tax_type= 'Exclusive' , 
			(i.amount *  i.total_tax_percentage  / 100) + i.amount  , 
			i.amount 
		) as sales_amount_exclusive  , 

		IF( s.tax_type= 'Inclusive' , 
			i.amount -  (i.amount *  i.total_tax_percentage  / 100)   , 
			0
		) as sales_amount_inclusive  , 

		IF( s.tax_type= 'Inclusive' , 
			i.amount -  (i.amount *  i.total_tax_percentage  / 100)   , 
			0
		) as return_amount_inclusive  , 

		IF( s.tax_type= 'Exclusive' , 
			 (i.amount *  i.total_tax_percentage  / 100) + i.amount  , 
			i.amount
		) as return_amount_exclusive  , 



		YEAR(s.posting_date) as year  , s.tax_type ,  i.total_tax_percentage 


		from `tabSales Invoice` s
		inner join 	`tabSales Invoice Item` i  on s.name = i.parent		
		inner join `tabSales Team` sp on s.name = sp.parent


		where 1=1 {}  order by s.posting_date desc """.format(conditions ), as_dict=1, debug=1)
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




def get_data_with_level_1_2_wtih_range(conditions = "", grouping_level_1 = "" , grouping_level_value_1 = "" , grouping_level_2 = "" , grouping_level_value_2 = "" ,   ranging_group = ""  ):
	if grouping_level_1:
		grouping_1 = grouping_level_1.get("grouping")
		numbering_1 = grouping_level_1.get("numbering")



		if grouping_level_2:
			grouping_2 = grouping_level_2.get("grouping")
			numbering_2 = grouping_level_2.get("numbering")

			if ranging_group:
				grouping = ranging_group.get("grouping")
				numbering = ranging_group.get("numbering")

				active_filter = ranging_group.get("active_filter")
				sorting = ranging_group.get("sorting")

				ranges = ranging_group.get("ranges")

			data =  frappe.db.sql(""" select  {}   as level_1 , {} as level_2 , 
				concat('{}', '-', {}   , '-', YEAR(s.posting_date) ) as period , 
				{}   as numbering,
				{} as ranged,
				YEAR(s.posting_date) as year ,





				i.item_code  ,  i.item_name , i.item_group , 
				s.name as voucher_no , s.posting_date as transaction_date , 
				i.qty , 

				IF( s.tax_type= 'Exclusive' , 
					(i.amount *  i.total_tax_percentage  / 100) + i.amount  , 
					i.amount 
				) as sales_amount_exclusive  , 

				IF( s.tax_type= 'Inclusive' , 
					i.amount -  (i.amount *  i.total_tax_percentage  / 100)   , 
					0
				) as sales_amount_inclusive  , 

				IF( s.tax_type= 'Inclusive' , 
					i.amount -  (i.amount *  i.total_tax_percentage  / 100)   , 
					0
				) as return_amount_inclusive  , 

				IF( s.tax_type= 'Exclusive' , 
					 (i.amount *  i.total_tax_percentage  / 100) + i.amount  , 
					i.amount
				) as return_amount_exclusive  



				from `tabSales Invoice` s
				inner join 	`tabSales Invoice Item` i  on s.name = i.parent	
				inner join `tabSales Team` sp on s.name = sp.parent


				where 1=1  and   {}  = '{}'  and {} = '{}'  {} {}  {}
				order by {}   ,  {} , YEAR(s.posting_date) asc """.format( numbering_1 ,  numbering_2 , ranges , numbering , 
					numbering  , numbering    ,  numbering_1 , grouping_level_value_1 ,  numbering_2 , grouping_level_value_2 ,    conditions , grouping_1 , grouping , numbering_1 , numbering), as_dict=1, debug=1)		

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






	columns.append(
	{
	"fieldname": "voucher_no",
	"label": _("Voucher No"),
	"fieldtype": "Data",
	"width": 100
	})

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
	"options" : "Item Group",
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
	"fieldname": "tax_type",
	"label": _("Tax Type"),
	"options" : "Data",
	"width": 150
	})



	columns.append(
	{
	"fieldname": "total_tax_percentage",
	"label": _("Tax Percentage"),
	"options" : "Data",
	"width": 150
	})





	columns.append(
	{
	"fieldname": "sales_amount_exclusive",
	"label": _("Sales Amount Exclusive"),
	"options" : "Data",
	"width": 150
	})



	columns.append(
	{
	"fieldname": "sales_amount_inclusive",
	"label": _("Sales Inlusive"),
	"options" : "Currency",
	"width": 150
	})


	columns.append(
	{
	"fieldname": "return_amount_exclusive",
	"label": _("Return Sales Exlusive"),
	"options" : "Currency",
	"width": 150
	})


	columns.append(
	{
	"fieldname": "return_amount_inclusive",
	"label": _("Return Amount Inclusive"),
	"fieldtype": "Currency",
	"width": 150
	})



	columns.append(
	{
	"fieldname": "sales_to_inclusive",
	"label": _("Sales To Inclusive"),
	"options" : "Data",
	"width": 150
	})





	columns.append(
	{
	"fieldname": "amount",
	"label": _("Amount"),
	"options" : "Data",
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



	columns.append(
	{
	"fieldname": "territory",
	"label": _("Territory"),
	"fieldtype": "Link",
	"options" : "Territory",
	"width": 150
	})


	columns.append(
	{
	"fieldname": "customer",
	"label": _("Customer"),
	"fieldtype": "Link",
	"options" : "Customer",
	"width": 150
	})

	columns.append(
	{
	"fieldname": "project",
	"label": _("Project"),
	"fieldtype": "Link",
	"options" : "Project",
	"width": 150
	})

	columns.append(
	{
	"fieldname": "division",
	"label": _("Division"),
	"options" : "Data",
	"width": 150
	})

	columns.append(
	{
	"fieldname": "year",
	"label": _("Year"),
	"fieldtype": "Data",
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






def grouping_by_level_2(filters = None):
	grouping = ""
	sorting = ""
	numbering = ""
	if filters.get("level_2") and filters.get("level_2") != "":
		if filters.get("level_2")=='Customer':
			grouping += " s.customer"
			numbering = "s.customer"


		if filters.get("level_2")=='Item Group':
			grouping += " i.item_group"
			numbering = "i.item_group"


		if filters.get("level_2")=='Item':
			grouping += " i.item_code  "
			numbering = "i.item_code"



		if filters.get("level_2")=='Territory':
			grouping += " s.territory "
			numbering = "s.territory"


		if filters.get("level_2")=='Sales Person':
			grouping += " sp.sales_person  "
			numbering = "sp.sales_person"

		if filters.get("level_2")=='Division':
			grouping += " s.cost_center  "
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










# def get_range_group_for_columns(conditions = "", filters  = ""):
# 	query_string_level = ""

# 	query_string_group = ""

# 	query_string_sorting = ""

# 	query_string_range = ""



# 	if filters.level_1 and filters.level_1 != "":

# 		grouping_level_1 = grouping_by_level_1(filters)

# 		if grouping_level_1:
# 			grouping_1 = grouping_level_1.get("grouping")
# 			numbering_1 = grouping_level_1.get("numbering") # s.customer 

# 			query_string_level += " {} as level_1 ".format(numbering_1)


# 		if filters.level_2 and filters.level_2 != "":

# 			grouping_level_2 = grouping_by_level_2(filters)


# 			if grouping_level_2:
# 				grouping_2 = grouping_level_2.get("grouping")
# 				numbering_2 = grouping_level_2.get("numbering")


# 				query_string_level += "  , {} as level_2 ".format(numbering_2)



# 		if filters.range and filters.range != "":


# 			grouping_ranged = range_grouping(filters)


# 			grouping_range = ""
# 			sorting = ""
# 			numbering_range = ""
# 			ranges = ""

# 			if grouping_ranged:
# 				grouping_range = grouping_ranged.get("grouping_range")
# 				numbering_range = grouping_ranged.get("numbering") # s.customer 
# 				ranges = grouping_ranged.get("ranges") # s.customer 

# 				query_string_range +=  """ ,
# 							concat('{}', '-', {}   , '-', YEAR(s.posting_date) ) as period , 
# 							{}   as numbering,
# 							{} as ranged,
# 							YEAR(s.posting_date) as year """.format(ranges , numbering_range ,  numbering_range  , numbering_range )

# 				data =  frappe.db.sql(""" select  DISTINCT  s.posting_date ,  {}  {}  
# 					from `tabSales Invoice` s
# 					inner join 	`tabSales Invoice Item` i  on s.name = i.parent	
# 					inner join `tabSales Team` sp on s.name = sp.parent
# 					where 1=1  {}  {} order by s.posting_date   """.format( query_string_level , query_string_range ,   conditions  , grouping_range   ), as_dict=1, debug=1)		

# 				return data








@frappe.whitelist()
def month_range(year, month):
	return calendar.monthrange(year, month)[1]



def get_month_name(num):
	months_name = {1 : "Jan",2 : "Feb",3 : "Mar",4 : "Apr",5 : "May",6 : "June",7 : "July",8 : "Aug",9 : "Sept",10 : "Oct",11 : "Nov",12 : "Dec"}
	return months_name.get(num)
