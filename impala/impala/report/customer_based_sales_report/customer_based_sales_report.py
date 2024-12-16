# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr
import numpy as np
import pandas as pd
import datetime
import json


def execute(filters=None):
    if not filters:
        filters = {}

    columns, data = get_columns(), []
    conditions = get_conditions(filters)
    data = get_data(filters, conditions)

    return columns, data



def get_data(filters, conditions):

	data = frappe.db.sql(""" 
			SELECT 
				si.customer, si.customer_name, si.cost_center, si.department, st.sales_person,
				SUM(sii.base_net_amount) as exclusive_amount, SUM(sii.base_amount) as inclusive_amount
			from
			 	`tabSales Invoice View` as si inner join `tabSales Invoice Item View` as sii on si.name = sii.parent
			 	left join `tabSales Team` as st on si.name=st.parent 
			where
				si.docstatus=1 {} GROUP BY si.customer, si.cost_center, si.department, st.sales_person
				ORDER BY si.customer, si.cost_center, si.department, st.sales_person
		""".format(conditions), as_dict=True, debug=False)

	return data


def get_columns():
	columns = [
		{
			"fieldname": "customer",
			"label":  _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 180,
		},
		{
			"fieldname": "customer_name",
			"label":  _("Customer Name"),
			"fieldtype": "Data",
			"width": 280,
		},
		{
			"fieldname": "sales_person",
			"label":  _("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
			"width": 240,
		},
		{
            "fieldname": "cost_center",
            "label": _("Division"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 200,
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 220,
        },
		{
			"fieldname": "exclusive_amount",
			"label":  _("Exclusive Amount"),
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"fieldname": "inclusive_amount",
			"label":  _("Inclusive Amount"),
			"fieldtype": "Currency",
			"width": 160
		}

	]

	return columns
def get_conditions(filters):
	conditions = ""
	if filters.company:
	    conditions += " and si.company = '{}'".format(filters.company)
	if filters.from_date:
	    conditions += " and si.posting_date BETWEEN '{}' AND '{}'".format(filters.from_date, filters.to_date)

	if filters.customer:
		customers = filters.customer
		if len(customers)<2:
		    customers.append("")
		customers = tuple(customers)
		conditions += " and si.customer IN {}".format(customers)
	
	if filters.customer_group:
		customer_groups = filters.customer_group
		if len(customer_groups)<2:
		    customer_groups.append("")
		customer_groups = tuple(customer_groups)
		conditions += " and si.customer_group IN {}".format(customer_groups)

	if filters.cost_center:
		cost_centers = filters.cost_center
		if len(cost_centers)<2:
			cost_centers.append("")
		cost_centers = tuple(cost_centers)
		conditions += "and si.cost_center IN {}".format(cost_centers)

	if filters.department:
		departments = filters.department
		if len(departments)<2:
			departments.append("")
		departments = tuple(departments)
		conditions += " and si.department IN {}".format(departments)
	
	if filters.sales_person:
		sales_persons = filters.sales_person
		if len(sales_persons)<2:
			sales_persons.append("")
		sales_persons = tuple(sales_persons)
		conditions += " and st.sales_person IN {}".format(sales_persons)
	
	if filters.item_code:
		items = filters.item_code
		if len(items)<2:
			items.append("")
		items = tuple(items)
		conditions += " and sii.item_code IN {}".format(items)

	if filters.item_group:
		item_groups = filters.item_group
		if len(item_groups)<2:
			item_groups.append("")
		item_groups = tuple(item_groups)
		conditions += " and (SELECT item_group from `tabItem` WHERE `tabItem`.item_code = sii.item_code) IN {}".format(item_groups)

	return conditions
