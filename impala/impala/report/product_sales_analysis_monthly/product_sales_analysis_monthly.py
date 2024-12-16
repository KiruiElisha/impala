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

		grouping_level_2 = grouping_by_level_2(filters) 
 
		grouping_level_3 = grouping_by_level_3(filters) 

		ranging_group = range_grouping(filters) 

		values_query = get_values_column(conditions = conditions , filters = filters)







		# frappe.msgprint(cstr(grouping_level_1))
		level_1 = group_level_1(conditions = conditions , grouping_level_1 = grouping_level_1 , filters = filters)
		# frappe.msgprint(cstr(level_1))

		if level_1:
			if not filters.get("level_2") and not filters.get("level_3") and  not filters.get("value") and not filters.get("range"):
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

						"item_code" : b.get("item_code") or "",
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

			elif filters.get("level_1") and  filters.get("level_2") and not filters.get("level_3") and  not filters.get("value") and not filters.get("range"):
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






			elif filters.get("level_1") and  filters.get("level_2") and  filters.get("level_3") and  not filters.get("value") and not filters.get("range"):
				# frappe.msgprint("Level 1 and level 2 and level 3 ")
				for i in level_1:
					data.append({"level_1" : i.get("level_1") })
					level_2  = group_level_2(conditions = "" , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , grouping_level_2 = grouping_level_2)
					for b in level_2:
						data.append({"level_2" : b.get("level_2") })

						level_3 = group_level_3(conditions = conditions, grouping_level_1 =  grouping_level_1 , grouping_level_value_1 = i.get("level_1") ,  
							grouping_level_2 = grouping_level_2 ,  grouping_level_value_2 = b.get("level_2") , grouping_level_3 = grouping_level_3  )
						for c in level_3:
							data.append({"level_3" : c.get("level_3") })
							level_3_child = group_level_3_3(conditions = conditions , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , 
								grouping_level_2  = grouping_level_2 , grouping_level_value_2 = b.get("level_2") ,   grouping_level_3  = grouping_level_3 , grouping_level_value_3 = c.get("level_3") ,  )
							for d in level_3_child:
								row = {
								"period" : d.get("period") or "",
								"ranging" : d.get("ranging") or "",
								"ranges" : d.get("ranges") or "",
								"year" : d.get("year") or "",

								"division" : d.get("division") or "",
								"territory" : d.get("territory") or "",
								"sales_person" : d.get("sales_person") or "",	
								"customer" : d.get("customer") or "",

								"item_code" : d.get("item_code") or "",
								"item_group" : d.get("item_group") or "",


								"voucher_no" : b.get("voucher_no") or "",

								"transaction_date" : d.get("transaction_date") or "",
								"qty" : d.get("qty") or "",	
								"amount_exclusive" : d.get("amount_exclusive") or "",
								"item_cost" : d.get("item_cost") or "",
								"amount_inclusive" : d.get("amount_inclusive") or "",
								"gross_profit" : d.get("gross_profit") or "",
								"gp" : d.get("gp") or "",
								"value" : d.get("value") or "",
								}
								data.append(row)


			elif filters.get("level_1")  and  filters.get("range") and not filters.get("level_2") :
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


			elif filters.get("level_1")  and  filters.get("level_2")  and  filters.get("range") and not filters.get("level_3") :
				ranging_group = range_grouping(filters)

				# frappe.msgprint("Level 1 and level 2 and level 3 ")
				for i in level_1:
					data.append({"level_1" : i.get("level_1") })
					main_group_level_1 = frappe.scrub(i.get("level_1")) # customer -- Waliullah  map_group = {}




					level_2  = group_level_2(conditions = "" , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , grouping_level_2 = grouping_level_2)
					for b in level_2:
						level_1_row = {}

						# data.append({"level_2" : b.get("level_2")})
						main_group_level_2 = frappe.scrub(b.get("level_2")) # customer -- Waliullah  map_group = {}
						range_level_1 = get_data_with_level_1_2_wtih_range(conditions = conditions , grouping_level_1 = grouping_level_1 , grouping_level_value_1 = i.get("level_1") , 
							grouping_level_2 = grouping_level_2 , grouping_level_value_2 = b.get("level_2") ,   ranging_group = ranging_group , values_query = values_query )



						for c in range_level_1:
							row = {}
							mrow  ={}
							child_group = c.get("period")
							if main_group_level_2 in map_group:
								print("main Group --- ")
								if child_group in main_group_level_2:
									value_exist = main_group_level_2.get(c.get("period"))
									value_exist =+ c.value
									map_group[main_group_level_2].update({ c.get("period") :  value_exist }) 
									print("")
								else:
									print("add Child ")
									map_group[main_group_level_2][c.get("period")] = c.value

							else:
								print("Main Group not Found. ")
								map_group[main_group_level_2] = {child_group :  c.value } 


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
							# data.append(row)

						level_1_row = map_group.get(main_group_level_2)
						level_1_row["level_2"]  =  b.get("level_2") 

						data.append(level_1_row)	













			elif filters.get("level_1")  and  filters.get("level_2")  and  filters.get("range") and  filters.get("level_3") :

				# frappe.msgprint("Level 1 and level 2 and level 3 ")
				for i in level_1:
					data.append({"level_1" : i.get("level_1") })
					main_group_level_1 = frappe.scrub(i.get("level_1")) # customer -- Waliullah  map_group = {}

					level_2  = group_level_2(conditions = "" , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , grouping_level_2 = grouping_level_2)
					for b in level_2:
						data.append({"level_2" : b.get("level_2")})
						main_group_level_2 = frappe.scrub(b.get("level_2")) # customer -- Waliullah  map_group = {}
						level_3 = group_level_3(conditions = conditions, grouping_level_1 =  grouping_level_1 , grouping_level_value_1 = i.get("level_1") ,  
							grouping_level_2 = grouping_level_2 ,  grouping_level_value_2 = b.get("level_2") , grouping_level_3 = grouping_level_3  )
						
						for c in level_3:
							# data.append({"level_3" : c.get("level_3") })
							level_1_row = {}
							main_group_level_3 = frappe.scrub(c.get("level_3")) # customer -- Waliullah  map_group = {}

							range_level_1 = get_data_with_level_1_2_3_wtih_range(conditions = conditions , grouping_level_1 = grouping_level_1 , grouping_level_value_1 = i.get("level_1") , 
								grouping_level_2 = grouping_level_2 , grouping_level_value_2 = b.get("level_2") ,   grouping_level_3 = grouping_level_3 , 
								grouping_level_value_3 = c.get("level_3")  ,  ranging_group = ranging_group , values_query = values_query )

							for d in range_level_1:

								row = {}
								mrow  ={}
								child_group = d.get("period")
								if main_group_level_3 in map_group:
									print("main Group --- ")
									if child_group in main_group_level_3:
										value_exist = main_group_level_3.get(d.get("period"))
										value_exist =+ c.value
										map_group[main_group_level_3].update({ d.get("period") :  value_exist }) 
										print("")
									else:
										print("add Child ")
										map_group[main_group_level_3][d.get("period")] = d.value  
								else:
									print("Main Group not Found. ")
									map_group[main_group_level_3] = {child_group :  d.value } 

								row = {
								"period" :d.get("period") or "",
								"ranging" : d.get("ranging") or "",
								"ranges" : d.get("ranges") or "",
								"year" : d.get("year") or "",

								"division" : d.get("division") or "",
								"territory" : d.get("territory") or "",
								"sales_person" : d.get("sales_person") or "",	
								"customer" : d.get("customer") or "",

								"item_code" : d.get("item_code") or "",
								"item_group" : d.get("item_group") or "",


								"transaction_date" : d.get("transaction_date") or "",
								"qty" : d.get("qty") or "",	
								"amount_exclusive" : d.get("amount_exclusive") or "",
								"item_cost" : d.get("item_cost") or "",
								"amount_inclusive" : d.get("amount_inclusive") or "",
								"gross_profit" : d.get("gross_profit") or "",
								"gp" : d.get("gp") or "",
								"value" : d.get("value") or "",
								}
								# data.append(row)
							level_1_row = map_group.get(main_group_level_3)
							level_1_row["level_3"]  =  c.get("level_3") 

							data.append(level_1_row)	






		new_col = get_range_group_for_columns(conditions = conditions , filters = filters)
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
	return conditions



def group_level_1(conditions = "" , grouping_level_1 = None, range_by = None , filters = None):
	data = []
	if grouping_level_1:
		grouping = grouping_level_1.get("grouping")
		numbering = grouping_level_1.get("numbering")

		data =  frappe.db.sql(""" select {}  as level_1 , 
			YEAR(s.transaction_date) as year 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent
			inner join `tabSales Team` sp on s.name = sp.parent
			where 1=1 {}   {}  order by s.transaction_date desc """.format( numbering ,  conditions , grouping), as_dict=1, debug=1)									
	return data

# when level 2 filres is not active data will be fetch base on level group. as inner records. 
def group_level_1_1(conditions = "" , grouping_level_1 = None,  grouping_level_value  = None, range_by = None , filters = None):
	if grouping_level_1:
		grouping = grouping_level_1.get("grouping")
		numbering = grouping_level_1.get("numbering")
		data =  frappe.db.sql(""" select  {} as level_1,  s.transaction_date, s.name  as voucher_no , i.item_code , i.qty , 

			(i.amount *  i.total_tax_percentage  / 100)  as amount_exclusive , 
			s.tax_type ,  i.total_tax_percentage ,


			i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
			i.amount as gp,  s.territory , s.customer , s.project ,  s.cost_center as division ,
			YEAR(s.transaction_date) as year 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent		
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and {} = '{}' {}   order by s.transaction_date desc """.format(numbering , numbering , grouping_level_value , conditions  ), as_dict=1, debug=1)
	return data



def group_level_2(conditions = "" , grouping_level_1  = "", grouping_level_value_1 = "" , grouping_level_2  = ""):


	if grouping_level_1:
		grouping_1 = grouping_level_1.get("grouping")
		numbering_1 = grouping_level_1.get("numbering")


		if grouping_level_2:
			grouping_2 = grouping_level_2.get("grouping")
			numbering_2 = grouping_level_2.get("numbering")

			data =  frappe.db.sql(""" select  {} as level_1 ,  {} as level_2  ,
			YEAR(s.transaction_date) as year 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and {} = '{}' {}  {} , {} order by s.transaction_date desc 
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
			YEAR(s.transaction_date) as year ,
			s.transaction_date, s.name  
 			as voucher_no , i.item_code , i.qty , 

			(i.amount *  i.total_tax_percentage  / 100) as amount_exclusive , 
			s.tax_type ,  i.total_tax_percentage ,


 			i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
 			i.amount as gp,  s.territory , s.customer , s.project ,  s.cost_center as division 


			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and {} = '{}' and  {} = '{}'  {}   order by s.transaction_date desc 
			""".format(numbering_1 , numbering_2 , numbering_1	 , grouping_level_value_1 , numbering_2  , grouping_level_value_2 , conditions  ), as_dict=1, debug=1)									
			return data





def group_level_3_3(conditions = "" , 
	grouping_level_1  = "", grouping_level_value_1 = "" , 
	grouping_level_2  = "" , grouping_level_value_2 = "" , 
	grouping_level_3  = "" , grouping_level_value_3 = ""  ):

	if grouping_level_1:
		grouping_1 = grouping_level_1.get("grouping")
		numbering_1 = grouping_level_1.get("numbering")

		if grouping_level_2:
			grouping_2 = grouping_level_2.get("grouping")
			numbering_2 = grouping_level_2.get("numbering")



			if grouping_level_3:
				grouping_3 = grouping_level_3.get("grouping")
				numbering_3 = grouping_level_3.get("numbering")


				data =  frappe.db.sql(""" select  {} as level_1 ,  {} as level_2  , {} as level_3 , 
				YEAR(s.transaction_date) as year ,
				s.transaction_date, s.name  
	 			as voucher_no , i.item_code , i.qty , 

				(i.amount *  i.total_tax_percentage  / 100) as amount_exclusive , 

				s.tax_type ,  i.total_tax_percentage ,

	 			i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
	 			i.amount as gp,  s.territory , s.customer , s.project ,  s.cost_center as division 


				from `tabSales Order` s
				inner join 	`tabSales Order Item` i  on s.name = i.parent
				inner join `tabSales Team` sp on s.name = sp.parent

				where 1=1  and {} = '{}' and  {} = '{}'  and {} = '{}' {}   order by s.transaction_date desc 
				""".format(numbering_1 , numbering_2 , numbering_3	 , 

					numbering_1 , grouping_level_value_1 , 
					numbering_2  , grouping_level_value_2 , 
					numbering_3  , grouping_level_value_3 , 

					conditions  ), as_dict=1, debug=1)									
				return data





# # when level 2 filres is not active data will be fetch base on level group. as inner records. 
# def group_level_2_2(conditions = "" , grouping_level_1 = None,  grouping_level_value  = None, range_by = None , filters = None):
# 	if grouping_level_1:
# 		grouping = grouping_level_1.get("grouping")
# 		numbering = grouping_level_1.get("numbering")
# 		data =  frappe.db.sql(""" select  {} as level_1,  
			# s.transaction_date, s.name  
# 			as voucher_no , i.item_code , i.qty , 
# 			i.amount as amount_exclusive , i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
# 			i.amount as gp,  s.territory , s.customer , s.project ,  s.cost_center as division ,
# 			YEAR(s.transaction_date) as year 
# 			from `tabSales Order` s
# 			inner join 	`tabSales Order Item` i  on s.name = i.parent		
# 			inner join `tabSales Team` sp on s.name = sp.parent

# 			where 1=1  and {} = '{}' {}   order by s.transaction_date desc """.format(numbering , numbering , grouping_level_value , conditions  ), as_dict=1, debug=1)
# 	return data










def group_level_3(conditions = "", grouping_level_1 = "" , grouping_level_value_1 = "" ,  grouping_level_2 = "" ,  grouping_level_value_2 = "" , grouping_level_3 = ""  ):
	if grouping_level_1:
		grouping_1 = grouping_level_1.get("grouping")
		numbering_1 = grouping_level_1.get("numbering")


		if grouping_level_2:
			grouping_2 = grouping_level_2.get("grouping")
			numbering_2 = grouping_level_2.get("numbering")



			if grouping_level_3:
				grouping_3 = grouping_level_3.get("grouping")
				numbering_3 = grouping_level_3.get("numbering")



				data =  frappe.db.sql(""" select  {} as level_1 ,  {} as level_2  , {} as level_3,
				YEAR(s.transaction_date) as year 
				from `tabSales Order` s
				inner join 	`tabSales Order Item` i  on s.name = i.parent
				inner join `tabSales Team` sp on s.name = sp.parent

				where 1=1  and {} = '{}'  and {} = '{}'  {}  {} , {} order by s.transaction_date desc 
				""".format(numbering_1 , numbering_2 , numbering_3 ,   
					numbering_1	 , grouping_level_value_1 , 
					numbering_2	 , grouping_level_value_2 ,
					conditions , grouping_1  , grouping_2 ,  grouping_3 ), as_dict=1, debug=1)									
				return data






def get_data_normal(conditions   = "", filters = ""):
		data =  frappe.db.sql(""" select  s.transaction_date, s.name  

			as voucher_no , i.item_code , i.qty ,  i.amount as amount , sp.sales_person , 

			i.amount  as amount_exclusive , 





			i.amount as item_cost,  i.amount as amount_inclusive ,i.amount as gross_profit ,
			i.amount as gp,  s.territory , s.customer , s.project ,  s.cost_center as division ,
			YEAR(s.transaction_date) as year  , s.tax_type ,  i.total_tax_percentage 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent		

			inner join `tabSales Team` sp on s.name = sp.parent			
			where 1=1 {}  order by s.transaction_date desc """.format(conditions ), as_dict=1, debug=1)
		return data



def get_data_with_level_1_2(conditions   = "", filters = "" , level_1 = "" , level_2 = ""):
		data =  frappe.db.sql(""" select  sum(i.qty) as qty , 
			YEAR(s.transaction_date) as year 
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent		
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and s.customer = '{}' and i.item_code = '{}' {}  order by s.transaction_date desc """.format( level_1 , level_2 , conditions), as_dict=1, debug=1)									
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
			concat('{}', '-', {}   , '-', YEAR(s.transaction_date) ) as period , 
			{}   as numbering,
			{} as ranged,
			YEAR(s.transaction_date) as year ,
			
			sum(i.qty) as qty 
			{}
			from `tabSales Order` s
			inner join 	`tabSales Order Item` i  on s.name = i.parent	
			inner join `tabSales Team` sp on s.name = sp.parent

			where 1=1  and   {}  = '{}' {} {}  {}
			order by {}  asc,   s.transaction_date asc ,  {} asc , YEAR(s.transaction_date) asc """.format( numbering_1 , ranges , numbering , 
				numbering  , numbering   , values_query , numbering_1  ,  grouping_level_value_1 , conditions , grouping_1 , grouping , numbering_1 , numbering), as_dict=1, debug=1)		

		return data




def get_data_with_level_1_2_wtih_range(conditions = "", grouping_level_1 = "" , grouping_level_value_1 = "" , grouping_level_2 = "" , grouping_level_value_2 = "" ,   ranging_group = ""  , values_query = "" ):
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
				concat('{}', '-', {}   , '-', YEAR(s.transaction_date) ) as period , 
				{}   as numbering,
				{} as ranged,
				YEAR(s.transaction_date) as year ,

				sum(i.qty) as qty 
				{}
				from `tabSales Order` s
				inner join 	`tabSales Order Item` i  on s.name = i.parent	
				inner join `tabSales Team` sp on s.name = sp.parent


				where 1=1  and   {}  = '{}'  and {} = '{}'  {} {}  {}
				order by {}   ,  {} , YEAR(s.transaction_date) asc """.format( numbering_1 ,  numbering_2 , ranges , numbering , 
					numbering  , numbering   , values_query ,  numbering_1 , grouping_level_value_1 ,  numbering_2 , grouping_level_value_2 ,    conditions , grouping_1 , grouping , numbering_1 , numbering), as_dict=1, debug=1)		

			return data




def get_data_with_level_1_2_3_wtih_range(conditions = "", grouping_level_1 = "" , grouping_level_value_1 = "" , grouping_level_2 = "" , 
	grouping_level_value_2 = "" ,   grouping_level_3 = "" , grouping_level_value_3 = "" ,   ranging_group = ""  , values_query = ""  ):
	if grouping_level_1:
		grouping_1 = grouping_level_1.get("grouping")
		numbering_1 = grouping_level_1.get("numbering")



		if grouping_level_2:
			grouping_2 = grouping_level_2.get("grouping")
			numbering_2 = grouping_level_2.get("numbering")




			if grouping_level_3:
				grouping_3 = grouping_level_3.get("grouping")
				numbering_3 = grouping_level_3.get("numbering")


				if ranging_group:
					grouping = ranging_group.get("grouping")
					numbering = ranging_group.get("numbering")

					active_filter = ranging_group.get("active_filter")
					sorting = ranging_group.get("sorting")

					ranges = ranging_group.get("ranges")

				data =  frappe.db.sql(""" select  {}   as level_1 , {} as level_2 , {} as level_3,  
					concat('{}', '-', {}   , '-', YEAR(s.transaction_date) ) as period , 
					{}   as numbering,
					{} as ranged,
					YEAR(s.transaction_date) as year ,
					sum(i.qty) as qty 
					{}
					from `tabSales Order` s
					inner join 	`tabSales Order Item` i  on s.name = i.parent
					inner join `tabSales Team` sp on s.name = sp.parent


					where 1=1  and   {}  = '{}'  and {} = '{}' and {} = '{}'   {} {}  {}
					order by {}   ,  {} , YEAR(s.transaction_date) asc """.format( numbering_1 ,  numbering_2 , numbering_3 ,  ranges , numbering , 
						numbering  , numbering   ,  values_query ,   numbering_1 , grouping_level_value_1 ,  numbering_2 , grouping_level_value_2 , numbering_3 , grouping_level_value_3 ,      conditions , grouping_1 , grouping , numbering_1 , numbering), as_dict=1, debug=1)		

				return data





def get_columns(conditions,filters , get_range_group_for_columns = "" ):
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

	if filters.level_3:
		columns.append(
		{
		"fieldname": "level_3",
		"label": filters.level_3,
		"fieldtype": "Data",
		"width": 100
		})





	if not filters.range:

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



	else:

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





		# columns.append(
		# {
		# "fieldname": "period",
		# "label": _("period"),
		# "fieldtype": "Data",
		# "width": 100
		# })


		# columns.append(
		# {
		# "fieldname": "numbering",
		# "label": _("numbering"),
		# "fieldtype": "Data",
		# "width": 100
		# })


		# columns.append(
		# {
		# "fieldname": "ranged",
		# "label": _("ranged"),
		# "fieldtype": "Data",
		# "width": 100
		# })


		# columns.append(
		# {
		# "fieldname": "year",
		# "label": _("Year"),
		# "fieldtype": "Data",
		# "width": 100
		# })




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




def grouping_by_level_3(filters = None):
	grouping = ""
	sorting = ""
	numbering = ""
	if filters.get("level_3") and filters.get("level_3") != "":
		if filters.get("level_3")=='Customer':
			grouping += "s.customer"
			numbering = "s.customer"


		if filters.get("level_3")=='Item Group':
			grouping += "i.item_group"
			numbering = "i.item_group"


		if filters.get("level_3")=='Item':
			grouping += "i.item_code  "
			numbering = "i.item_code"



		if filters.get("level_3")=='Territory':
			grouping += "s.territory "
			numbering = "s.territory"


		if filters.get("level_3")=='Sales Person':
			grouping += " sp.sales_person  "
			numbering = "sp.sales_person"

		if filters.get("level_3")=='Division':
			grouping += "s.cost_center  "
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
			grouping += ",WEEK(s.transaction_date),  YEAR(s.transaction_date)"
			grouping_range += " group by  WEEK(s.transaction_date),  YEAR(s.transaction_date)"
			sorting += ",WEEK(s.transaction_date) asc"
			numbering = "WEEK(s.transaction_date)"
			ranges = "Week"

		if filters.get("range")=='Month':
			grouping +=  ",MONTH(s.transaction_date),  YEAR(s.transaction_date) "
			grouping_range +=  " group by  MONTH(s.transaction_date),  YEAR(s.transaction_date) "
			sorting += ",MONTH(s.transaction_date) asc , YEAR(s.transaction_date) "
			numbering = "MONTH(s.transaction_date)"
			ranges = "Month"


		if filters.get("range")=='Year':
			grouping +=  ",YEAR(s.transaction_date) "
			grouping_range +=  " group by YEAR(s.transaction_date) "
			sorting += ",YEAR(s.transaction_date) asc"
			ranges = "Year"
			numbering = "YEAR(s.transaction_date)"


		if filters.get("range")=='Quarter':
			grouping +=  ",Quarter(s.transaction_date) "
			grouping_range +=  " group by Quarter(s.transaction_date) "
			sorting += ",Quarter(s.transaction_date) asc"
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
		if filters.get("value") == "qty":
			values+= " , sum(i.qty) as value "
			# frappe.msgprint("Qty is Selected Filters".format(values))
		if filters.get("value") == "amount_exclusive":
			values+= " , sum((i.amount *  i.total_tax_percentage  / 100))   as value "
		if filters.get("value") == "amount_inclusive":
			values+= " , sum(i.amount) as value "
	else:
		values+= " , sum(i.qty) as value"
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


		if filters.level_2 and filters.level_2 != "":

			grouping_level_2 = grouping_by_level_2(filters)


			if grouping_level_2:
				grouping_2 = grouping_level_2.get("grouping")
				numbering_2 = grouping_level_2.get("numbering")


				query_string_level += "  , {} as level_2 ".format(numbering_2)



			if filters.level_3 and filters.level_3 != "":
				grouping_level_3 = grouping_by_level_3(filters)

				if grouping_level_3:
					grouping_3 = grouping_level_3.get("grouping")
					numbering_3 = grouping_level_3.get("numbering")


					query_string_level += "  , {} as level_3 ".format(numbering_3)



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

				data =  frappe.db.sql(""" select  DISTINCT  s.transaction_date ,  {}  {}  
					from `tabSales Order` s
					inner join 	`tabSales Order Item` i  on s.name = i.parent	
					inner join `tabSales Team` sp on s.name = sp.parent
					where 1=1  {}  {} order by s.transaction_date   """.format( query_string_level , query_string_range ,   conditions  , grouping_range   ), as_dict=1, debug=1)		

				return data








@frappe.whitelist()
def month_range(year, month):
	return calendar.monthrange(year, month)[1]



def get_month_name(num):
	months_name = {1 : "Jan",2 : "Feb",3 : "Mar",4 : "Apr",5 : "May",6 : "June",7 : "July",8 : "Aug",9 : "Sept",10 : "Oct",11 : "Nov",12 : "Dec"}
	return months_name.get(num)
