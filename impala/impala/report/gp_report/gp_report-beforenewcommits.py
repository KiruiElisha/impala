# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr
import numpy as np
import pandas as pd
import datetime
import json
import itertools
from collections import defaultdict
import pandas as pd
import time

def execute(filters=None):
    if not filters:
        filters = {}

    columns, data = get_columns(), []
    if filters.get("group_by") == 'Item':
    	columns.pop(1)
    conditions = get_conditions(filters)
    query = get_data(filters, conditions)
    result_obj = {}
    for d in query:
    	result_obj.setdefault(d.item_code, {'description' : d.item_name, 'qty':0.0, 'base_amount' : 0.0, 'base_net_amount':0.0, 'item_cost':0.0, 'gross_profit':0.0}) \
    	if filters.get("group_by") == 'Item' else result_obj.setdefault(d.name, {'description' : d.name, 'qty':0.0, 'base_amount' : 0.0, 'base_net_amount':0.0, 'item_cost':0.0, 'gross_profit':0.0})

    for r in query:
    	gkey = r.name if filters.get("group_by")=='Voucher' else r.item_code
    	result_obj[gkey]['customer'] = r.customer
    	result_obj[gkey]['qty'] += r.qty
    	result_obj[gkey]['base_amount'] += r.base_amount
    	result_obj[gkey]['base_net_amount'] += r.base_net_amount
    	result_obj[gkey]['item_cost'] += r.item_cost
    	result_obj[gkey]['gross_profit'] += r.gross_profit

    for key, val in result_obj.items():
    	row = {}
    	row['description'] = val['description']
    	row['customer'] = val['customer']
    	row['qty'] = val['qty']
    	row['base_amount'] = val['base_amount']
    	row['base_net_amount'] = val['base_net_amount']
    	row['item_cost'] = val['item_cost']
    	row['gross_profit'] = val['gross_profit']
    	row['gp_percent'] = round((val['gross_profit']*100 / (val['base_net_amount'] if val['base_net_amount'] !=0 else 1.0)),2)
    	data.append(row)
    	

    return columns, data



def get_data(filters, conditions):

	data = frappe.db.sql("""
			SELECT 
			si.name, sii.item_code, CONCAT(sii.item_code, ' ', sii.item_name) as item_name, sii.description, CONCAT(si.customer, ' ', si.customer_name) as customer,
			sii.qty, sii.base_amount, sii.base_net_amount,
			IFNULL((select `tabStock Ledger Entry`.valuation_rate from `tabStock Ledger Entry` where `tabStock Ledger Entry`.item_code = sii.item_code and 
			`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and
			 `tabStock Ledger Entry`.warehouse=sii.warehouse and
			`tabStock Ledger Entry`.voucher_no = IF(si.update_stock=0, sii.delivery_note, sii.parent) limit 1)*IFNULL(sii.stock_qty,0.0),0.0) as item_cost,
			
			(sii.base_net_amount - IFNULL((select `tabStock Ledger Entry`.valuation_rate from `tabStock Ledger Entry` where `tabStock Ledger Entry`.item_code = sii.item_code and 
			`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and 
			`tabStock Ledger Entry`.warehouse = sii.warehouse and
			`tabStock Ledger Entry`.voucher_no = IF(si.update_stock=0, sii.delivery_note, sii.parent) limit 1)*IFNULL(sii.stock_qty, 0.0), 0.0)) as gross_profit
			
			from `tabSales Invoice View` as si inner join `tabSales Invoice Item View` as sii on si.name = sii.parent 
			where si.docstatus=1 {}
		""".format(conditions), as_dict=True, debug=False)
	return data




def get_columns():
	columns = [
		{
			"fieldname": "description",
			"label":  _("Description"),
			"fieldtype": "Data",
			"width": 320,
			"align": "left",
		},
		{
			"fieldname": "customer",
			"label":  _("Customer"),
			"fieldtype": "Data",
			"width": 220,
			"align": "left",
		},
		{
			"fieldname": "qty",
			"label":  _("Qty"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "base_amount",
			"label":  _("Amount"),
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"fieldname": "base_net_amount",
			"label":  _("Net Amount"),
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"fieldname": "item_cost",
			"label":  _("Item Cost"),
			"fieldtype": "Currency",
			"width": 160
		},	
		{
			"fieldname": "gross_profit",
			"label":  _("Gross Profit"),
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"fieldname": "gp_percent",
			"label":  _("Gross Profit %"),
			"fieldtype": "Percentage",
			"width": 120
		},

	]

	return columns
def get_conditions(filters):
	conditions = ""
	if filters.company:
	    conditions += " and si.company = '{}'".format(filters.company)
	if filters.from_date:
	    conditions += " and si.posting_date BETWEEN '{}' AND '{}'".format(filters.from_date, filters.to_date)
	
	if filters.voucher_no:
		voucher_nos = filters.voucher_no
		if len(voucher_nos)<2:
			voucher_nos.append("")
		voucher_nos = tuple(voucher_nos)
		conditions += " and si.name IN {}".format(voucher_nos)


	if filters.item_code:
		items = filters.item_code
		if len(items)<2:
			items.append("")
		items = tuple(items)
		conditions += " and sii.item_code IN {}".format(items)

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

	if filters.customer:
		customers = filters.customer
		if len(customers)<2:
			customers.append("")
		customers = tuple(customers)
		conditions += " and si.customer IN {}".format(customers)
		
	return conditions
