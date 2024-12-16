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
	 

from frappe.utils import getdate, cstr, fmt_money
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

		level_1 = group_level_1(conditions = conditions , grouping_level_1 = grouping_level_1 , filters = filters)

		if level_1:
			if not filters.get("level_2") and not filters.get("level_3") and  not filters.get("value") and not filters.get("range"):
				grandTotals = {"level_1": "<h4>Grand Totals<h4>", "amount" : 0.0, "qty" : 0, "item_cost": 0.0, "amount_exclusive" : 0.0, "amount_inclusive" : 0.0, "gross_profit" : 0.0}
				for i in level_1:
					subTotals = {"level_1": "<h4>Sub Totals L1<h4>", "amount" : 0.0, "qty" : 0, "item_cost": 0.0, "amount_exclusive" : 0.0, "amount_inclusive" : 0.0, "gross_profit" : 0.0}
					data.append({"level_1" : i.get("level_1")})
					level_1_child = group_level_1_1(conditions = conditions , grouping_level_1 = grouping_level_1,  grouping_level_value  = i.get("level_1"))
					for b in level_1_child:
						
						row = {
						"period" : b.get("period") or "",
						"ranging" : b.get("ranging") or "",
						"ranges" : b.get("ranges") or "",
						"year" : b.get("year") or "",

						"division" : b.get("division") or "",
						"department" : b.get("department") or "",
						"territory" : b.get("territory") or "",
						"sales_person" : b.get("sales_person") or "",	
						"customer" : b.get("customer") or "",
						"local_and_international" : b.get("local_and_international") or "",

						"item_code" : b.get("item_code") or "",
						"item_name" : b.get("item_name") or "",
						"status" : b.get("status") or "",
						"item_group" : b.get("item_group") or "",
						"voucher_no" : b.get("voucher_no") or "",
						"tax_type" : b.get("tax_type") or "",
						"total_tax_percentage" : b.get("total_tax_percentage") or "",
						"amount" : fmt_money(b.get("amount") or 0.0, currency=b.currency) or "",


						"transaction_date" : b.get("transaction_date") or "",
						"qty" : b.get("qty") or "",	
						"amount_exclusive" :  fmt_money(b.get("amount_exclusive") or 0.0, currency=b.currency) or "",
						"item_cost" : fmt_money(b.get("item_cost") or 0.0, currency=b.currency) or "",
						"amount_inclusive" :  fmt_money(b.get("amount_inclusive") or 0.0, currency=b.currency) or "",
						"gross_profit" : fmt_money((b.get("amount_exclusive") or 0.0) - (b.get("item_cost") or 0.0), currency=b.currency) or "",
						"gp" : round((((b.get("amount_exclusive") or 0.0) - (b.get("item_cost") or 0.0))/(b.get("item_cost") or 1.0))*100, 2) or "", #gp = (GP/Cost)*100
						"value" : b.get("value") or "",
						}

						subTotals["qty"] += b.get("qty") or 0.0
						subTotals["amount"] += b.get("amount") or 0.0
						subTotals["amount_exclusive"] +=b.get("amount_exclusive") or 0.0
						subTotals["amount_inclusive"] += b.get("amount_inclusive") or 0.0
						subTotals["item_cost"] += b.get("item_cost") or 0.0
						subTotals["gross_profit"] += (b.get("amount_exclusive") or 0.0) - (b.get("item_cost") or 0.0)
						# subTotals["gp"] += (((b.get("amount_exclusive") or 0.0) - (b.get("item_cost") or 0.0))/(b.get("item_cost") or 1.0))*100

						grandTotals["qty"] += b.get("qty") or 0.0
						grandTotals["amount"] += b.get("amount") or 0.0
						grandTotals["amount_exclusive"] +=b.get("amount_exclusive") or 0.0
						grandTotals["amount_inclusive"] += b.get("amount_inclusive") or 0.0
						grandTotals["item_cost"] += b.get("item_cost") or 0.0
						grandTotals["gross_profit"] += (b.get("amount_exclusive") or 0.0) - (b.get("item_cost") or 0.0)
						# grandTotals["gp"] += (((b.get("amount_exclusive") or 0.0) - (b.get("item_cost") or 0.0))/(b.get("item_cost") or 1.0))*100

						data.append(row)
					data.append(subTotals)
				data.append(grandTotals)

			elif filters.get("level_1") and  filters.get("level_2") and not filters.get("level_3") and  not filters.get("value") and not filters.get("range"):
				# frappe.msgprint("Level 1 and level 2 ")
				print("")

				grandTotals = {"level_1": "<h4>Grand Totals<h4>", "amount" : 0.0, "qty" : 0, "item_cost": 0.0, "amount_exclusive" : 0.0, "amount_inclusive" : 0.0, "gross_profit" : 0.0}

				for i in level_1:
					subTotals1 = {"level_1": "<h4>Sub Totals L1</h4>", "amount" : 0.0, "qty" : 0, "item_cost": 0.0, "amount_exclusive" : 0.0, "amount_inclusive" : 0.0, "gross_profit" : 0.0}
					data.append({"level_1" : i.get("level_1")})
					level_2  = group_level_2(conditions = "" , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , grouping_level_2 = grouping_level_2)
					for b in level_2:
						data.append({"level_2" : b.get("level_2")})
						level_2_child = group_level_2_2(conditions = conditions , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , 
							grouping_level_2  = grouping_level_2 , grouping_level_value_2 = b.get("level_2") )
						subTotals2 = {"level_2": "<h5>Sub Totals L2</h5>", "amount" : 0.0, "qty" : 0, "item_cost": 0.0, "amount_exclusive" : 0.0, "amount_inclusive" : 0.0, "gross_profit" : 0.0}
						for c in level_2_child:

							subTotals1["qty"] += c.get("qty") or 0.0
							subTotals1["amount"] += c.get("amount") or 0.0
							subTotals1["amount_exclusive"] +=c.get("amount_exclusive") or 0.0
							subTotals1["amount_inclusive"] += c.get("amount_inclusive") or 0.0
							subTotals1["item_cost"] += c.get("item_cost") or 0.0
							subTotals1["gross_profit"] += (c.get("amount_exclusive") or 0.0) - (c.get("item_cost") or 0.0)
							# subTotals1["gp"] += (((c.get("amount_exclusive") or 0.0) - (c.get("item_cost") or 0.0))/(c.get("item_cost") or 1.0))*100

							subTotals2["qty"] += c.get("qty") or 0.0
							subTotals2["amount"] += c.get("amount") or 0.0
							subTotals2["amount_exclusive"] +=c.get("amount_exclusive") or 0.0
							subTotals2["amount_inclusive"] += c.get("amount_inclusive") or 0.0
							subTotals2["item_cost"] += c.get("item_cost") or 0.0
							subTotals2["gross_profit"] += (c.get("amount_exclusive") or 0.0) - (c.get("item_cost") or 0.0)
							# subTotals2["gp"] += (((c.get("amount_exclusive") or 0.0) - (c.get("item_cost") or 0.0))/(c.get("item_cost") or 1.0))*100


							grandTotals["qty"] += c.get("qty") or 0.0
							grandTotals["amount"] += c.get("amount") or 0.0
							grandTotals["amount_exclusive"] +=c.get("amount_exclusive") or 0.0
							grandTotals["amount_inclusive"] += c.get("amount_inclusive") or 0.0
							grandTotals["item_cost"] += c.get("item_cost") or 0.0
							grandTotals["gross_profit"] += (c.get("amount_exclusive") or 0.0) - (c.get("item_cost") or 0.0)
							# grandTotals["gp"] += (((c.get("amount_exclusive") or 0.0) - (c.get("item_cost") or 0.0))/(c.get("item_cost") or 1.0))*100

							row = {
							"period" : c.get("period") or "",
							"ranging" : c.get("ranging") or "",
							"ranges" : c.get("ranges") or "",
							"year" : c.get("year") or "",

							"division" : c.get("division") or "",
							"department" : c.get("department") or "",
							"territory" : c.get("territory") or "",
							"sales_person" : c.get("sales_person") or "",	
							"customer" : c.get("customer") or "",
							"local_and_international" : c.get("local_and_international") or "",

							"item_code" : c.get("item_code") or "",
							"item_group" : c.get("item_group") or "",
							"item_name" : c.get("item_name") or "",
							"status" : c.get("status") or "",
							"voucher_no" : c.get("voucher_no") or "",

							"tax_type" : c.get("tax_type") or "",
							"total_tax_percentage" : c.get("total_tax_percentage") or "",
							"amount" : fmt_money(c.get("amount") or 0.0, currency=c.currency) or "",
							"transaction_date" : c.get("transaction_date") or "",
							"qty" : c.get("qty") or "",	
							"amount_exclusive" : fmt_money(c.get("amount_exclusive") or 0.0, currency=c.currency) or "",
							"item_cost" : fmt_money(c.get("item_cost") or 0.0, currency=c.currency) or "",
							"amount_inclusive" : fmt_money(c.get("amount_inclusive") or 0.0, currency=c.currency) or "",
							"gross_profit" : fmt_money((c.get("amount_exclusive") or 0.0) - (c.get("item_cost") or 0.0), currency=c.currency) or "",
							"gp" : round((((c.get("amount_exclusive") or 0.0) - (c.get("item_cost") or 0.0))/(c.get("item_cost") or 1.0))*100, 2) or "",
							"value" : c.get("value") or "",
							}

							data.append(row)
						data.append(subTotals2)
					data.append(subTotals1)
				data.append(grandTotals)





			elif filters.get("level_1") and  filters.get("level_2") and  filters.get("level_3") and  not filters.get("value") and not filters.get("range"):
				grandTotals = {"level_1": "<h4>Grand Totals</h4>", "amount" : 0.0, "qty" : 0, "item_cost": 0.0, "amount_exclusive" : 0.0, "amount_inclusive" : 0.0, "gross_profit" : 0.0}
				for i in level_1:
					subTotals1 = {"level_1": "<h4>Sub Totals L1</h4>", "amount" : 0.0, "qty" : 0, "item_cost": 0.0, "amount_exclusive" : 0.0, "amount_inclusive" : 0.0, "gross_profit" : 0.0}
					data.append({"level_1" : i.get("level_1") })
					level_2  = group_level_2(conditions = "" , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , grouping_level_2 = grouping_level_2)
					for b in level_2:
						subTotals2 = {"level_2": "<h5>Sub Totals L2</h5>", "amount" : 0.0, "qty" : 0, "item_cost": 0.0, "amount_exclusive" : 0.0, "amount_inclusive" : 0.0, "gross_profit" : 0.0}
						data.append({"level_2" : b.get("level_2") })

						level_3 = group_level_3(conditions = conditions, grouping_level_1 =  grouping_level_1 , grouping_level_value_1 = i.get("level_1") ,  
							grouping_level_2 = grouping_level_2 ,  grouping_level_value_2 = b.get("level_2") , grouping_level_3 = grouping_level_3  )
						for c in level_3:
							subTotals3 = {"level_3": "<h6>Sub Totals L3</h6>", "amount" : 0.0, "qty" : 0, "item_cost": 0.0, "amount_exclusive" : 0.0, "amount_inclusive" : 0.0, "gross_profit" : 0.0}
							data.append({"level_3" : c.get("level_3") })
							level_3_child = group_level_3_3(conditions = conditions , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , 
								grouping_level_2  = grouping_level_2 , grouping_level_value_2 = b.get("level_2") ,   grouping_level_3  = grouping_level_3 , grouping_level_value_3 = c.get("level_3") ,  )
							for d in level_3_child:

								subTotals1["qty"] += d.get("qty") or 0.0
								subTotals1["amount"] += d.get("amount") or 0.0
								subTotals1["amount_exclusive"] +=d.get("amount_exclusive") or 0.0
								subTotals1["amount_inclusive"] += d.get("amount_inclusive") or 0.0
								subTotals1["item_cost"] += d.get("item_cost") or 0.0
								subTotals1["gross_profit"] += (d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0)
								# subTotals1["gp"] += (((d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0))/(d.get("item_cost") or 1.0))*100

								subTotals2["qty"] += d.get("qty") or 0.0
								subTotals2["amount"] += d.get("amount") or 0.0
								subTotals2["amount_exclusive"] +=d.get("amount_exclusive") or 0.0
								subTotals2["amount_inclusive"] += d.get("amount_inclusive") or 0.0
								subTotals2["item_cost"] += d.get("item_cost") or 0.0
								subTotals2["gross_profit"] += (d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0)
								# subTotals2["gp"] += (((d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0))/(d.get("item_cost") or 1.0))*100

								subTotals3["qty"] += d.get("qty") or 0.0
								subTotals3["amount"] += d.get("amount") or 0.0
								subTotals3["amount_exclusive"] +=d.get("amount_exclusive") or 0.0
								subTotals3["amount_inclusive"] += d.get("amount_inclusive") or 0.0
								subTotals3["item_cost"] += d.get("item_cost") or 0.0
								subTotals3["gross_profit"] += (d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0)
								# subTotals3["gp"] += (((d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0))/(d.get("item_cost") or 1.0))*100

								grandTotals["qty"] += d.get("qty") or 0.0
								grandTotals["amount"] += d.get("amount") or 0.0
								grandTotals["amount_exclusive"] +=d.get("amount_exclusive") or 0.0
								grandTotals["amount_inclusive"] += d.get("amount_inclusive") or 0.0
								grandTotals["item_cost"] += d.get("item_cost") or 0.0
								grandTotals["gross_profit"] += (d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0)
								# grandTotals["gp"] += (((d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0))/(d.get("item_cost") or 1.0))*100

								row = {
								"period" : d.get("period") or "",
								"ranging" : d.get("ranging") or "",
								"ranges" : d.get("ranges") or "",
								"year" : d.get("year") or "",

								"division" : d.get("division") or "",
								"department" : d.get("department") or "",
								"territory" : d.get("territory") or "",
								"sales_person" : d.get("sales_person") or "",	
								"customer" : d.get("customer") or "",
								"local_and_international" : d.get("local_and_international") or "",

								"item_code" : d.get("item_code") or "",
								"item_group" : d.get("item_group") or "",

								"item_name" : d.get("item_name") or "",
								"status" : d.get("status") or "",

								"voucher_no" : d.get("voucher_no") or "",


								"tax_type" : d.get("tax_type") or "",
								"total_tax_percentage" : d.get("total_tax_percentage") or "",
								"amount" : fmt_money(d.get("amount") or 0.0, currency=d.currency) or "",
								"transaction_date" : d.get("transaction_date") or "",
								"qty" : d.get("qty") or "",	
								"amount_exclusive" : fmt_money(d.get("amount_exclusive") or 0.0, currency=d.currency) or "",
								"item_cost" : fmt_money(d.get("item_cost") or 0,0, currency=d.currency) or "",
								"amount_inclusive" : fmt_money(d.get("amount_inclusive") or 0.0, currency=d.currency) or "",
								"gross_profit" : fmt_money((d.get("amount_exclusive") or 0.0)-(d.get("item_cost") or 0.0), currency=d.currency) or "",
								"gp" : round((((d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0))/(d.get("item_cost") or 1.0))*100, 2) or "",
								"value" : d.get("value") or "",
								}
								data.append(row)
							data.append(subTotals3)
						data.append(subTotals2)
					data.append(subTotals1)
				data.append(grandTotals)

			elif filters.get("level_1")  and  filters.get("range") and not filters.get("level_2") :
				ranging_group = range_grouping(filters)

		
				for i in level_1:
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
							
							if b.get("value") and type(b.get("value")) == 'str':
									myVal = float(b.get("value").replace(",", ""))
							else:
								myVal = b.get("value")
							row = {
							main_group  : main_group  , 
							b.get("period")  : b.get("period") , 
							"qty" : b.get("value") or "",	
							"value" : myVal,
							}
							

						level_1_row = map_group.get(main_group)
						level_1_row["level_1"]  =  i.get("level_1") 
						data.append(level_1_row)

			elif filters.get("level_1")  and  filters.get("level_2")  and  filters.get("range") and not filters.get("level_3") :
				ranging_group = range_grouping(filters)


				for i in level_1:
					data.append({"level_1" : i.get("level_1") })
					main_group_level_1 = frappe.scrub(i.get("level_1")) # customer -- Waliullah  map_group = {}

					level_2  = group_level_2(conditions = "" , grouping_level_1  = grouping_level_1, grouping_level_value_1 = i.get("level_1") , grouping_level_2 = grouping_level_2)
					

					for b in level_2:
						level_1_row = {}

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

							if c.get("value") and type(c.get("value")) == 'str':
									myVal = float(c.get("value").replace(",", ""))
							else:
								myVal = b.get("value")

							row = {
							"period" :c.get("period") or "",
							"ranging" : c.get("ranging") or "",
							"ranges" : c.get("ranges") or "",
							"year" : c.get("year") or "",

							"division" : c.get("division") or "",
							"department" : c.get("department") or "",
							"territory" : c.get("territory") or "",
							"sales_person" : c.get("sales_person") or "",	
							"customer" : c.get("customer") or "",
							"local_and_international" : c.get("local_and_international") or "",

							"item_code" : c.get("item_code") or "",
							"item_group" : c.get("item_group") or "",

							"voucher_no" : c.get("voucher_no") or "",


							"tax_type" : c.get("tax_type") or "",
							"total_tax_percentage" : c.get("total_tax_percentage") or "",
							"amount" : fmt_money(c.get("amount") or 0.0, currency=c.currency) or "",



							"item_name" : c.get("item_name") or "",
							"status" : c.get("status") or "",



							"transaction_date" : c.get("transaction_date") or "",
							"qty" : c.get("qty") or "",	
							"amount_exclusive" : fmt_money(c.get("amount_exclusive") or 0.0, currency=c.currency) or "",
							"item_cost" : fmt_money(c.get("item_cost") or 0.0, currency=c.currency) or "",
							"amount_inclusive" : fmt_money(c.get("amount_inclusive") or 0.0, currency=c.currency) or "",
							"gross_profit" : fmt_money((c.get("amount_exclusive") or 0.0) - (c.get("item_cost") or 0.0), currency=c.currency) or "",
							"gp" : round((((c.get("amount_exclusive") or 0.0) - (c.get("item_cost") or 0.0))/(c.get("item_cost") or 1.0))*100, 2) or "",
							"value" : fmt_money(myVal, currency=c.currency),
							}

						if map_group.get(main_group_level_2):
							level_1_row = map_group.get(main_group_level_2)

						
						level_1_row["level_2"]  =  b.get("level_2") 

						data.append(level_1_row)

					


			elif filters.get("level_1")  and  filters.get("level_2")  and  filters.get("range") and  filters.get("level_3") :
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

								if d.get("value") and type(d.get("value")) == 'str':
									myVal = float(d.get("value").replace(",", ""))
								else:
									myVal = d.get("value")

								row = {
								"period" :d.get("period") or "",
								"ranging" : d.get("ranging") or "",
								"ranges" : d.get("ranges") or "",
								"year" : d.get("year") or "",

								"division" : d.get("division") or "",
								"department" : d.get("department") or "",
								"territory" : d.get("territory") or "",
								"sales_person" : d.get("sales_person") or "",	
								"customer" : d.get("customer") or "",
								# "local_and_international" : d.get("local_and_international") or "",

								"item_code" : d.get("item_code") or "",
								"item_group" : d.get("item_group") or "",
								"voucher_no" : d.get("voucher_no") or "",

								"tax_type" : d.get("tax_type") or "",
								"total_tax_percentage" : d.get("total_tax_percentage") or "",
								"amount" : fmt_money(d.get("amount") or 0.0, currency=d.currency) or "",

								"item_name" : d.get("item_name") or "",
								"status" : d.get("status") or "",

								"transaction_date" : d.get("transaction_date") or "",
								"qty" : d.get("qty") or "",	
								"amount_exclusive" : fmt_money(d.get("amount_exclusive") or 0.0, currency=d.currency) or "",
								"item_cost" : fmt_money(d.get("item_cost") or 0.0, currency=d.currency) or "",
								"amount_inclusive" : fmt_money(d.get("amount_inclusive") or 0.0, currency=d.currency) or "",
								"gross_profit" : fmt_money((d.get("amount_exclusive") or 0.0)-(d.get("item_cost") or 0.0), currency=d.currency) or "",
								"gp" : round((((d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0))/(d.get("item_cost") or 1.0))*100, 2) or "",
								"value" : myVal,
								}


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

	return columns , data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.posting_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and s.posting_date <=  '{}' ".format(filters.get("to_date"))
	if filters.get("status"):
		conditions += " and s.status =  '{}' ".format(filters.get("status"))
	if filters.get("company"):
		conditions += " and s.company =  '{}' ".format(filters.get("company"))
	if filters.get("local_and_international"):
		conditions += " and c.local_and_international =  '{}' ".format(filters.get("local_and_international"))

	return conditions



def group_level_1(conditions = "" , grouping_level_1 = None, range_by = None , filters = None):
	data = []
	if grouping_level_1:
		grouping = grouping_level_1.get("grouping")
		numbering = grouping_level_1.get("numbering")

		data =  frappe.db.sql(""" select {}  as level_1 , 
			YEAR(s.posting_date) as year, c.local_and_international as local_and_international 
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent
			inner join `tabSales Team` sp on s.name = sp.parent
			inner join `tabCustomer` c on s.customer = c.name
			where s.docstatus=1 and s.is_return=0 {}   {}  order by s.posting_date desc """.format( numbering ,  conditions , grouping), as_dict=1)									
	return data

# when level 2 filres is not active data will be fetch base on level group. as inner records. 
def group_level_1_1(conditions = "" , grouping_level_1 = None,  grouping_level_value  = None, range_by = None , filters = None):
	if grouping_level_1:
		grouping = grouping_level_1.get("grouping")
		numbering = grouping_level_1.get("numbering")
		data =  frappe.db.sql(""" select  {} as level_1,  s.posting_date, s.name  
			as voucher_no , i.item_code , i.item_name ,     i.qty , 
			s.tax_type ,  i.total_tax_percentage ,  i.item_group ,
			i.amount as amount, i.net_amount as amount_exclusive, i.base_amount as amount_inclusive, 
			(select b.valuation_rate from `tabBin` b where b.item_code = i.item_code and b.warehouse=i.warehouse)*i.qty as item_cost,
			i.amount as gross_profit,
			i.amount as gp,  s.territory , s.customer_name as customer, s.project ,  s.cost_center as division, s.department as department,  
			c.local_and_international as local_and_international, YEAR(s.posting_date) as year  , s.status
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent		
			inner join `tabSales Team` sp on s.name = sp.parent
			inner join `tabCustomer` c on s.customer = c.name
			where s.docstatus=1 and s.is_return=0 and {} = '{}' {}   order by s.posting_date desc """.format(numbering , numbering , grouping_level_value , conditions  ), as_dict=1)
	return data



def group_level_2(conditions = "" , grouping_level_1  = "", grouping_level_value_1 = "" , grouping_level_2  = ""):


	if grouping_level_1:
		grouping_1 = grouping_level_1.get("grouping")
		numbering_1 = grouping_level_1.get("numbering")


		if grouping_level_2:
			grouping_2 = grouping_level_2.get("grouping")
			numbering_2 = grouping_level_2.get("numbering")

			data =  frappe.db.sql(""" select  {} as level_1 ,  {} as level_2  ,
			YEAR(s.posting_date) as year, c.local_and_international as local_and_international
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent
			inner join `tabSales Team` sp on s.name = sp.parent
			inner join `tabCustomer` c on s.customer = c.name
			where s.docstatus=1 and s.is_return=0  and {} = '{}' {}  {} , {} order by s.posting_date desc 
			""".format(numbering_1 , numbering_2 , numbering_1	 , grouping_level_value_1 , conditions , grouping_1  , grouping_2  ), as_dict=1)									
			return data



def group_level_2_2(conditions = "" , grouping_level_1  = "", grouping_level_value_1 = "" , grouping_level_2  = "" , grouping_level_value_2 = ""):
	if grouping_level_1:
		grouping_1 = grouping_level_1.get("grouping")
		numbering_1 = grouping_level_1.get("numbering")

		if grouping_level_2:
			grouping_2 = grouping_level_2.get("grouping")
			numbering_2 = grouping_level_2.get("numbering")

			data =  frappe.db.sql(""" select  {} as level_1 ,  {} as level_2  ,
			YEAR(s.posting_date) as year ,
			s.posting_date, s.name as voucher_no, s.currency as currency, i.item_code , i.item_name ,   i.qty , 
			s.tax_type ,  i.total_tax_percentage ,  i.item_group ,
			i.amount as amount, i.net_amount as amount_exclusive, i.base_amount as amount_inclusive, 
			(select b.valuation_rate from `tabBin` b where b.item_code = i.item_code and b.warehouse=i.warehouse)*i.qty as item_cost,
 			i.amount as gross_profit , c.local_and_international as local_and_international,
 			i.amount as gp,  s.territory , s.customer_name as customer, s.project ,  s.cost_center as division,s.department as department, s.status
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent
			inner join `tabSales Team` sp on s.name = sp.parent
			inner join `tabCustomer` c on s.customer = c.name
			where s.docstatus=1 and s.is_return=0  and {} = '{}' and  {} = '{}'  {}   order by s.posting_date desc 
			""".format(numbering_1 , numbering_2 , numbering_1	 , grouping_level_value_1 , numbering_2  , grouping_level_value_2 , conditions  ), as_dict=1)									
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
				YEAR(s.posting_date) as year ,
				s.posting_date, s.name as voucher_no, s.currency as currency, i.item_code , i.item_name ,    i.qty , 
				s.tax_type ,  i.total_tax_percentage ,  i.item_group ,
				i.amount as amount, i.net_amount as amount_exclusive, i.base_amount as amount_inclusive, 
				(select b.valuation_rate from `tabBin` b where b.item_code = i.item_code and b.warehouse=i.warehouse)*i.qty as item_cost,
	 			i.amount as gross_profit , c.local_and_international as local_and_international,
	 			i.amount as gp,  s.territory , s.customer_name as customer, s.project ,  s.cost_center as division, s.department as department, s.status
				from `tabSales Invoice` s
				inner join 	`tabSales Invoice Item` i  on s.name = i.parent
				inner join `tabSales Team` sp on s.name = sp.parent
				inner join `tabCustomer` c on s.customer = c.name
				where s.docstatus=1 and s.is_return=0  and {} = '{}' and  {} = '{}'  and {} = '{}' {}   order by s.posting_date desc 
				""".format(numbering_1, numbering_2, numbering_3, numbering_1, grouping_level_value_1, numbering_2, grouping_level_value_2, 
					numbering_3, grouping_level_value_3, conditions), as_dict=1)									
				return data


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
				YEAR(s.posting_date) as year, c.local_and_international as local_and_international
				from `tabSales Invoice` s
				inner join 	`tabSales Invoice Item` i  on s.name = i.parent
				inner join `tabSales Team` sp on s.name = sp.parent
				inner join `tabCustomer` c on s.customer = c.name
				where s.docstatus=1 and s.is_return=0  and {} = '{}'  and {} = '{}'  {}  {} , {} order by s.posting_date desc 
				""".format(numbering_1 , numbering_2 , numbering_3 ,   
					numbering_1	 , grouping_level_value_1 , 
					numbering_2	 , grouping_level_value_2 ,
					conditions , grouping_1  , grouping_2 ,  grouping_3 ), as_dict=1)									
				return data






def get_data_normal(conditions   = "", filters = ""):
		data = []
		query =  frappe.db.sql(""" select  s.posting_date, s.name as voucher_no, s.currency as currency, i.item_code ,  i.item_name ,   i.qty ,  s.status ,   i.amount as amount , sp.sales_person , 
			s.tax_type ,  i.total_tax_percentage ,  i.item_group ,
			i.amount as amount, i.net_amount as amount_exclusive, i.base_amount as amount_inclusive, 
			(select b.valuation_rate from `tabBin` b where b.item_code = i.item_code and b.warehouse=i.warehouse)*i.qty as item_cost,
			i.amount as gross_profit, c.local_and_international as local_and_international,
			i.amount as gp,  s.territory , s.customer_name as customer, s.project ,  s.cost_center as division, s.department as department,
			YEAR(s.posting_date) as year  , s.tax_type ,  i.total_tax_percentage  , s.status
			from `tabSales Invoice` s
			inner join `tabSales Invoice Item` i  on s.name = i.parent
			inner join `tabSales Team` sp on s.name = sp.parent
			inner join `tabCustomer` c on s.customer = c.name			
			where s.docstatus=1 and s.is_return=0 {}  order by s.posting_date desc """.format(conditions ), as_dict=1)

		grandTotals = {"voucher_no": "<h4>Grand Totals<h4>", "amount" : 0.0, "qty" : 0, "item_cost": 0.0, "amount_exclusive" : 0.0, "amount_inclusive" : 0.0, "gross_profit" : 0.0}

		for d in query:

			row = {}
			row["voucher_no"] = d.get("voucher_no")
			row["item_code"] = d.get("item_code")
			row["item_name"] = d.get("item_name")
			row["qty"] = d.get("qty") or 0.0
			row["tax_type"] = d.get("tax_type") or ""
			row["total_tax_percentage"] = d.get("total_tax_percentage") or 0.0
			row["amount"] = d.get("amount") or 0.0
			row["amount_inclusive"] = d.get("amount_inclusive") or 0.0
			row["amount_exclusive"] = d.get("amount_exclusive") or 0.0
			row["item_cost"] = d.get("item_cost") or 0.0
			row["gross_profit"] = (d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0)
			row["gp"] = round((((d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0))/(d.get("item_cost") or 1))*100, 2) or ""
			row["territory"] = d.get("territory")
			row["customer"] = d.get("customer")
			row["project"] = d.get("project")
			row["division"] = d.get("division")
			row["department"] = d.get("department")
			row["year"] = d.get("year")
			row["status"] = d.get("status")
			row["local_and_international"] = d.get("local_and_international") or ""
			
			grandTotals["qty"] += d.get("qty") or 0.0
			grandTotals["amount"] += d.get("amount") or 0.0
			grandTotals["amount_exclusive"] += d.get("amount_exclusive") or 0.0
			grandTotals["amount_inclusive"] += d.get("amount_inclusive") or 0.0
			grandTotals["item_cost"] += d.get("item_cost") or 0.0
			grandTotals["gross_profit"] += (d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0)
			# grandTotals["gp"] += (((d.get("amount_exclusive") or 0.0) - (d.get("item_cost") or 0.0))/(d.get("item_cost") or 1.0))*100

			data.append(row)
		data.append(grandTotals)

		return data



def get_data_with_level_1_2(conditions   = "", filters = "" , level_1 = "" , level_2 = ""):
		data =  frappe.db.sql(""" select  sum(i.qty) as qty, 
			YEAR(s.posting_date) as year, c.local_and_international as local_and_international 
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent		
			inner join `tabSales Team` sp on s.name = sp.parent
			inner join `tabCustomer` c on s.customer = c.name
			where s.docstatus=1 and s.is_return=0  and s.customer_name = '{}' and i.item_code = '{}' {}  order by s.posting_date desc """.format( level_1 , level_2 , conditions), as_dict=1)									
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
			concat('{}', '-', {}   , '-', YEAR(s.posting_date) ) as period, c.local_and_international as local_and_international,  
			{}   as numbering,
			{} as ranged,
			YEAR(s.posting_date) as year ,
			
			sum(i.qty) as qty 
			{}
			from `tabSales Invoice` s
			inner join 	`tabSales Invoice Item` i  on s.name = i.parent	
			inner join `tabSales Team` sp on s.name = sp.parent
			inner join `tabCustomer` c on s.customer = c.name
			where s.docstatus=1 and s.is_return=0  and   {}  = '{}' {} {}  {}
			order by {}  asc,   s.posting_date asc ,  {} asc , YEAR(s.posting_date) asc """.format( numbering_1 , ranges , numbering , 
				numbering  , numbering   , values_query , numbering_1  ,  grouping_level_value_1 , conditions , grouping_1 , grouping , numbering_1 , numbering), as_dict=1, debug=True)		

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
				concat('{}', '-', {}   , '-', YEAR(s.posting_date) ) as period , c.local_and_international as local_and_international,
				{}   as numbering,
				{} as ranged,
				YEAR(s.posting_date) as year ,
				sum(i.qty) as qty 
				{}
				from `tabSales Invoice` s
				inner join 	`tabSales Invoice Item` i  on s.name = i.parent	
				inner join `tabSales Team` sp on s.name = sp.parent
				inner join `tabCustomer` c on s.customer = c.name
				where s.docstatus=1 and s.is_return=0  and   {}  = '{}'  and {} = '{}'  {} {}  {}
				order by {}   ,  {} , YEAR(s.posting_date) asc """.format( numbering_1 ,  numbering_2 , ranges , numbering , 
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
					concat('{}', '-', {}   , '-', YEAR(s.posting_date) ) as period , c.local_and_international as local_and_international,
					{}   as numbering,
					{} as ranged,
					YEAR(s.posting_date) as year ,
					sum(i.qty) as qty 
					{}
					from `tabSales Invoice` s
					inner join 	`tabSales Invoice Item` i  on s.name = i.parent
					inner join `tabSales Team` sp on s.name = sp.parent
					inner join `tabCustomer` c on s.customer = c.name
					where s.docstatus=1 and s.is_return=0  and   {}  = '{}'  and {} = '{}' and {} = '{}'   {} {}  {}
					order by {}   ,  {} , YEAR(s.posting_date) asc """.format( numbering_1 ,  numbering_2 , numbering_3 ,  ranges , numbering , 
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
		"options" : "Percentage",
		"width": 150
		})



		columns.append(
		{
		"fieldname": "amount",
		"label": _("Amount"),
		"fieldtype": "Currency",
		"options" : "Sales Invoice",
		"width": 150
		})


		columns.append(
		{
		"fieldname": "amount_inclusive",
		"label": _("Amount Inclusive"),
		"fieldtype": "Currency",
		"options" : "Sales Invoice",
		"width": 150
		})


		columns.append(
		{
		"fieldname": "amount_exclusive",
		"label": _("Amount Exclusive"),
		"fieldtype": "Currency",
		"options" : "Sales Invoice",
		"width": 150
		})


		columns.append(
		{
		"fieldname": "item_cost",
		"label": _("Item Cost"),
		"fieldtype": "Currency",
		"options" : "Sales Invoice",
		"width": 150
		})



		columns.append(
		{
		"fieldname": "gross_profit",
		"label": _("Gross Profit"),
		"fieldtype": "Currency",
		"options" : "Sales Invoice",
		"width": 150
		})



		columns.append(
		{
		"fieldname": "gp",
		"label": _("GP %"),
		"fieldtype": "Percentage",
		"options" : "Sales Invoice",
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
		"fieldname": "department",
		"label": _("Department"),
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


		columns.append(
		{
		"fieldname": "status",
		"label": _("Status"),
		"fieldtype": "Data",
		"width": 150
		})

		columns.append(
		{
		"fieldname": "local_and_international",
		"label": _("Local/International"),
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

	return columns


def grouping_by_level_1(filters):


	grouping = ""
	sorting = ""
	numbering = ""
	if filters.get("level_1") and filters.get("level_1") != "":
		if filters.get("level_1")=='Customer':
			grouping += "group by s.customer_name"
			numbering = "s.customer_name"

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

		if filters.get("level_1")=='Department':
			grouping += "group by s.department  "
			numbering = "s.department"

		if filters.get("level_1")=='Local/Export':
			grouping += "group by c.local_and_international "
			numbering = "c.local_and_international"

	return { "grouping" : grouping , "numbering" : numbering }


def grouping_by_level_2(filters = None):
	grouping = ""
	sorting = ""
	numbering = ""
	if filters.get("level_2") and filters.get("level_2") != "":
		if filters.get("level_2")=='Customer':
			grouping += " s.customer_name"
			numbering = "s.customer_name"

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

		if filters.get("level_2")=='Department':
			grouping += "s.department  "
			numbering = "s.department"

		if filters.get("level_2")=='Local/Export':
			grouping += "c.local_and_international  "
			numbering = "c.local_and_international"

	return { "grouping" : grouping , "numbering" : numbering }




def grouping_by_level_3(filters = None):
	grouping = ""
	sorting = ""
	numbering = ""
	if filters.get("level_3") and filters.get("level_3") != "":
		if filters.get("level_3")=='Customer':
			grouping += "s.customer_name"
			numbering = "s.customer_name"

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

		if filters.get("level_3")=='Department':
			grouping += "s.department  "
			numbering = "s.department"

		if filters.get("level_3")=='Local/Export':
			grouping += "c.local_and_international  "
			numbering = "c.local_and_international"

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
			values+= " , FORMAT(sum(i.qty), 2) as value "

		if filters.get("value") == "Amount Exclusive":
			values+= " , CONCAT('Sh ', FORMAT(SUM(i.net_amount), 2))  as value "

		if filters.get("value") == "Amount Inclusive":
			values+= """ , CONCAT('Sh ', FORMAT(SUM(i.base_amount), 2)) as value """


		# No need of these filters below #

		# if filters.get("value") == "Item Cost":
		# 	values+= """ , FORMAT((select b.valuation_rate from `tabBin` b where b.item_code = i.item_code and b.warehouse=i.warehouse)*SUM(i.qty) or 0.0), s.currency) as value """

		# if filters.get("value") == "GP":
		# 	# values+= """ , FORMAT(
		# 	# (
		# 	# 	SUM(i.net_amount) - ((select b.valuation_rate from `tabBin` b where b.item_code = i.item_code and b.warehouse=i.warehouse)*SUM(i.qty) or 0.0)
		# 	# )*100/
		# 	# (
		# 	# 	((select b.valuation_rate from `tabBin` b where b.item_code = i.item_code and b.warehouse=i.warehouse)*SUM(i.qty) or 1)
		# 	# ), s.currency
		# 	# ) as value """

		# 	values+= """ , FORMAT(
		# 	SUM(
		# 		(i.net_amount - ((select b.valuation_rate from `tabBin` b where b.item_code = i.item_code and b.warehouse=i.warehouse)*i.qty or 0.0))*100/
		# 		((select b.valuation_rate from `tabBin` b where b.item_code = i.item_code and b.warehouse=i.warehouse)*i.qty or 1)
		# 	), s.currency) as value """

		# if filters.get("value") == "Gross Profit":
		# 	# values+= """ , FORMAT(SUM(i.net_amount) - ((select SUM(b.valuation_rate) from `tabBin` b where b.item_code = i.item_code)*(i.qty) or 0.0), s.currency) as value """
		# 	values+= """ , (
		# 	SUM(i.net_amount) - 
		# 	(((select SUM(b.valuation_rate) from `tabBin` b where b.item_code = i.item_code) or 0.0)*(i.qty OR 0.0) )
		# 	) as value """
	
	else:
		values+= " , CONCAT('Sh ', FORMAT(SUM(i.net_amount),2))  as value "


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
			numbering_1 = grouping_level_1.get("numbering") # s.customer_name 

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
				numbering_range = grouping_ranged.get("numbering") # s.customer_name 
				ranges = grouping_ranged.get("ranges") # s.customer_name 

				query_string_range +=  """ ,
							concat('{}', '-', {}   , '-', YEAR(s.posting_date) ) as period , c.local_and_international as local_and_international,
							{}   as numbering,
							{} as ranged,
							YEAR(s.posting_date) as year """.format(ranges , numbering_range ,  numbering_range  , numbering_range )

				data =  frappe.db.sql(""" select  DISTINCT  s.posting_date ,  {}  {}  
					from `tabSales Invoice` s
					inner join 	`tabSales Invoice Item` i  on s.name = i.parent	
					inner join `tabSales Team` sp on s.name = sp.parent
					inner join 	`tabCustomer` c on s.customer = c.name
					where s.docstatus=1 and s.is_return=0  {}  {} order by s.posting_date   """.format( query_string_level , query_string_range ,   conditions  , grouping_range   ), as_dict=1)		

				return data



@frappe.whitelist()
def month_range(year, month):
	return calendar.monthrange(year, month)[1]



def get_month_name(num):
	months_name = {1 : "Jan",2 : "Feb",3 : "Mar",4 : "Apr",5 : "May",6 : "June",7 : "July",8 : "Aug",9 : "Sept",10 : "Oct",11 : "Nov",12 : "Dec"}
	return months_name.get(num)
