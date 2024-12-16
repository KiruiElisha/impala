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
	columns = get_columns(conditions , filters)
	data = get_data(conditions = conditions)

	return columns , data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and s.transaction_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("from_date"):
		conditions += " and s.transaction_date >= '{}' ".format(filters.get("from_date"))
	if filters.get("item_group"):
		conditions += " and i.item_group = '{}' ".format(filters.get("item_group"))
	if filters.get("item_code"):
		conditions += " and i.item_code = '{}' ".format(filters.get("item_code"))
	if filters.get("supplier"):
		conditions += " and s.supplier = '{}' ".format(filters.get("supplier"))
	if filters.get("cost_center"):
		conditions += " and s.cost_center = '{}' ".format(filters.get("cost_center"))
	if filters.get("company"):
		conditions += " and s.company =  '{}' ".format(filters.get("company"))

	if filters.get("project"):
		conditions += " and s.project =  '{}' ".format(filters.get("project"))

	return conditions



def get_data(conditions = ""):
	data =  frappe.db.sql(""" select  s.company , s.name as purchase_order , s.status , s.supplier ,  s.transaction_date ,
		i.ac_date , i.assign  , i.es  , i.new_es ,  i.notification_date , i.status as child_status  , i.task
		from `tabPurchase Order` s
		inner join 	`tabPurchase Order Task` i  on s.name = i.parent
		where 1=1 {} order by s.transaction_date desc """.format( conditions ), as_dict=1, debug=1)									
	return data






def get_columns(conditions,filters , ranging_group_column = "" ):
	columns = [
	{
	"fieldname": "purchase_order",
	"label": _("PO # "),
	"fieldtype": "Link",
	"options" : "Purchase Order",
	"width": 100
	},
	{
	"fieldname": "transaction_date",
	"label": _("Date"),
	"fieldtype": "date",
	"width": 100
	},



	{
	"fieldname": "ac_date",
	"label": _("AC Date "),
	"fieldtype": "Date",
	"width": 100
	},


	{
	"fieldname": "assign",
	"label": _("Assign"),
	"fieldtype": "Data",
	"width": 100
	},



	{
	"fieldname": "es",
	"label": _("ES"),
	"fieldtype": "Data",
	"width": 100
	},

	{

	"fieldname": "new_es",
	"label": _("New ES"),
	"fieldtype": "Data",
	"width": 100
	},

	{
	"fieldname": "notification_date",
	"label": _("Notification Date"),
	"fieldtype": "Data",
	"width": 100
	},

	{
	"fieldname": "child_status",
	"label": _("Child Status"),
	"fieldtype": "Data",
	"width": 100
	},


	{
	"fieldname": "task",
	"label": _("Task"),
	"fieldtype": "Data",
	"width": 100
	},


	{
	"fieldname": "supplier",
	"label": _("Supplier"),
	"fieldtype": "link",
	"options" : "Supplier",
	"width": 100
	},
	{
	"fieldname": "company",
	"label": _("Comapny"),
	"fieldtype": "link",
	"options" : "Company",
	"width": 100
	},

	]


	return columns



# @frappe.whitelist(allow_guest = True)
# def get_purchase_order_list(company):
# 	return frappe.db.get_list("Purchase Order" , {"company" : company , "docstatus" : ("!=" : 2) }, "name")


