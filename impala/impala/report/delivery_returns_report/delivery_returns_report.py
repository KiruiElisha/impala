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

    

    # df = pd.DataFrame(data[:5])

    # # table = pd.pivot_table(df.values.tolist(), index=['customer_name'], aggfunc = {'net_amount' : 'sum'})
    # # data = table.values.tolist()

    # frappe.msgprint(cstr(data))
    # # frappe.log_error(f"{df.values.tolist()}\n{df.columns.values.tolist()}", 'df values')
    # # columns = table.columns.values.tolist()




    return columns, data



def get_data(filters, conditions):

	data = frappe.db.sql(""" 
        SELECT dn.posting_date, dn.posting_time, dn.is_return, dn.local_and_international, dn.name, dn.cost_center, dn.department,
         dn.territory, dn.customer_name,dn.customer_group, dn.tax_type, dn.return_reason,dn.return_against,
         (SELECT `tabSales Team`.sales_person FROM `tabSales Team` WHERE `tabSales Team`.parent = dn.name LIMIT 1) AS sales_person,
        (SELECT item_group from `tabDelivery Note Item` where `tabDelivery Note Item`.item_code = dni.item_code LIMIT 1) as item_group,
        dni.item_code, dni.item_name,dni.pcs, dni.withholding_tax_amount, dni.withholding_vat_percentage, dni.qty, dni.stock_uom, dni.conversion_factor,
        dni.price_list_rate, dni.base_rate, dni.base_amount, dni.rate, dni.amount, dni.base_net_amount, dni.net_amount,
        (dni.base_amount*dni.total_tax_percentage/100) as total_tax_amount,        
        IFNULL((select `tabStock Ledger Entry`.valuation_rate from `tabStock Ledger Entry` where `tabStock Ledger Entry`.item_code = dni.item_code and 
        `tabStock Ledger Entry`.voucher_type IN ('Delivery Note') and 
        `tabStock Ledger Entry`.warehouse = dni.warehouse and
        `tabStock Ledger Entry`.voucher_no =  dni.parent LIMIT 1)*IFNULL(dni.stock_qty,0.0),0.0) as item_cost,
        
        (dni.base_net_amount - IFNULL((select `tabStock Ledger Entry`.valuation_rate from `tabStock Ledger Entry` where `tabStock Ledger Entry`.item_code = dni.item_code and 
        `tabStock Ledger Entry`.voucher_type IN ('Delivery Note') and 
        `tabStock Ledger Entry`.warehouse = dni.warehouse and
        `tabStock Ledger Entry`.voucher_no =  dni.parent LIMIT 1)*IFNULL(dni.stock_qty,0.0)*IFNULL(dni.stock_qty,0.0), 0.0)) as gross_profit,
        



        ROUND(
                (        
                    IFNULL(dni.base_net_amount, 0.0) -  
                    IFNULL((select `tabStock Ledger Entry`.valuation_rate from `tabStock Ledger Entry` where `tabStock Ledger Entry`.item_code = dni.item_code and 
			        `tabStock Ledger Entry`.voucher_type IN ('Delivery Note') and 
			        `tabStock Ledger Entry`.warehouse = dni.warehouse and
			        `tabStock Ledger Entry`.voucher_no =  dni.parent LIMIT 1)*IFNULL(dni.stock_qty,0.0)*IFNULL(dni.stock_qty,0.0),0.0)
                )*100/IFNULL(dni.base_net_amount, 1.0)
            ,2) as gp_percent


        FROM `tabDelivery Note` as dn inner join `tabDelivery Note Item` as dni on dn.name = dni.parent 
        WHERE dn.docstatus=1 and dn.is_return=1 {}
    """.format(conditions), as_dict=True, debug=False)


	return data


def get_columns():
	columns = [
		
		{
			"fieldname": "name",
			"label":  _("Voucher No"),
			"fieldtype": "Link",
			"options": "Delivery Note",
			"width": 100,
		},
		{
			"fieldname": "posting_date",
			"label":  _("Date"),
			"fieldtype": "Link",
			"options": "Delivery Note",
			"width": 100,
		},
		{
			"fieldname": "return_against",
			"label":  _("Against DN"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "customer_name",
			"label":  _("Customer"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "qty",
			"label":  _("Qty"),
			"fieldtype": "Float",
			"width": 80
		},
		{
			"fieldname": "base_rate",
			"label":  _("Rate"),
			"fieldtype": "Currency",
			"width": 80
		},
		{
			"fieldname": "item_cost",
			"label":  _("Item Cost"),
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "item_name",
			"label":  _("Item Name"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "return_reason",
			"label":  _("Return Reason"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "pcs",
			"label":  _("PCS"),
			"fieldtype": "Data",
			"width": 50,
		},
		{
			"fieldname": "stock_uom",
			"label":  _("Stock UOM"),
			"fieldtype": "Data",
			"width": 50,
		},
		{
			"fieldname": "sales_person",
			"label":  _("Sales Person"),
			"fieldtype": "Data",			
			"width": 150,
		},
		{
			"fieldname": "local_and_international",
			"label":  _("Local/Export"),
			"fieldtype": "Data",
			"width": 100,
		},
		# {
		# 	"fieldname": "item_code",
		# 	"label":  _("Item Code"),
		# 	"fieldtype": "Link",
		# 	"options": "Item",
		# 	"width": 150
		# },
		
		# {
		# 	"fieldname": "item_group",
		# 	"label":  _("Item Group"),
		# 	"fieldtype": "Data",
		# 	"width": 150,
		# },
		
		

		
		# {
		# 	"fieldname": "base_amount",
		# 	"label":  _("Amount"),
		# 	"fieldtype": "Currency",
		# 	"width": 100
		# },
		# {
		# 	"fieldname": "base_net_amount",
		# 	"label":  _("Net Amount"),
		# 	"fieldtype": "Currency",
		# 	"width": 100
		# },
		# {
		# 	"fieldname": "tax_type",
		# 	"label":  _("Tax Type"),
		# 	"fieldtype": "Data",
		# 	"width": 100
		# },
		# {
		# 	"fieldname": "total_tax_amount",
		# 	"label":  _("Total Tax Amount"),
		# 	"fieldtype": "Currency",
		# 	"width": 100
		# },
		# {
		# 	"fieldname": "withholding_tax_amount",
		# 	"label":  _("WTH Tax Amount"),
		# 	"fieldtype": "Currency",
		# 	"width": 100
		# },
		# {
		# 	"fieldname": "withholding_vat_percentage",
		# 	"label":  _("WTH %"),
		# 	"fieldtype": "Percentage",
		# 	"width": 100
		# },
			
		# {
		# 	"fieldname": "gross_profit",
		# 	"label":  _("Gross Profit"),
		# 	"fieldtype": "Currency",
		# 	"width": 100
		# },
		# {
		# 	"fieldname": "gp_percent",
		# 	"label":  _("Gross Profit %"),
		# 	"fieldtype": "Percentage",
		# 	"width": 100
		# },

        # {
        #     "fieldname": "cost_center",
        #     "label": _("Division"),
        #     "fieldtype": "Link",
        #     "options": "Cost Center",
        #     "width": 100,
        # },
        # {
        #     "fieldname": "department",
        #     "label": _("Department"),
        #     "fieldtype": "Link",
        #     "options": "Department",
        #     "width": 100,
        # },
        # {
        #     "fieldname": "territory",
        #     "label": _("Territory"),
        #     "fieldtype": "Link",
        #     "options": "Territory",
        #     "width": 100,
        # },

	]

	return columns
def get_conditions(filters):
	conditions = ""
	if filters.company:
	    conditions += " and dn.company = '{}'".format(filters.company)
	if filters.from_date:
	    conditions += " and dn.posting_date BETWEEN '{}' AND '{}'".format(filters.from_date, filters.to_date)

	if filters.customer:
		customers = filters.customer
		if len(customers)<2:
		    customers.append("")
		customers = tuple(customers)
		conditions += " and dn.customer IN {}".format(customers)
	
	if filters.customer_group:
		customer_groups = filters.customer_group
		if len(customer_groups)<2:
		    customer_groups.append("")
		customer_groups = tuple(customer_groups)
		conditions += " and dn.customer_group IN {}".format(customer_groups)

	if filters.cost_center:
		cost_centers = filters.cost_center
		if len(cost_centers)<2:
			cost_centers.append("")
		cost_centers = tuple(cost_centers)
		conditions += "and dn.cost_center IN {}".format(cost_centers)

	if filters.department:
		departments = filters.department
		if len(departments)<2:
			departments.append("")
		departments = tuple(departments)
		conditions += " and dn.department IN {}".format(departments)
	
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
		conditions += " and dni.item_code IN {}".format(items)

	if filters.item_group:
		item_groups = filters.item_group
		if len(item_groups)<2:
			item_groups.append("")
		item_groups = tuple(item_groups)
		conditions += " and (SELECT item_group from `tabItem` WHERE `tabItem`.item_code = dni.item_code) IN {}".format(item_groups)
	if filters.name:
	    conditions += " and dn.name = '{}'".format(filters.name)

	return conditions














# SELECT
#     dni.item_name as 'Item',
#     ROUND(SUM(dni.qty), 2) AS Quantity,
#     ROUND(SUM(dni.base_amount), 2) AS 'Exclusive Amount', SUM(dni.base_net_amount) AS 'Inclusive Amount',
#     ROUND(IFNULL((select 
#             SUM(`tabStock Ledger Entry`.valuation_rate) from `tabStock Ledger Entry`
#             where `tabStock Ledger Entry`.item_code = dni.item_code and 
# 			`tabStock Ledger Entry`.warehouse=dni.warehouse and 
# 			`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and 
# 			`tabStock Ledger Entry`.voucher_no = IF(dn.update_stock=0, dni.delivery_note, dni.parent)
# 			GROUP BY `tabStock Ledger Entry`.item_code limit 1)*SUM(dni.stock_qty), 0.0), 2) as 'Item Cost',
			
# 	ROUND(IFNULL(dni.base_amount - (select 
#             SUM(`tabStock Ledger Entry`.valuation_rate) from `tabStock Ledger Entry`
#             where `tabStock Ledger Entry`.item_code = dni.item_code and 
# 			`tabStock Ledger Entry`.warehouse=dni.warehouse and 
# 			`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and 
# 			`tabStock Ledger Entry`.voucher_no = IF(dn.update_stock=0, dni.delivery_note, dni.parent)
# 			GROUP BY `tabStock Ledger Entry`.item_code limit 1)*SUM(dni.stock_qty), 0.0), 2) as 'Gross Profit',
    
#     ROUND(IFNULL(SUM(dni.base_amount) - (select SUM(`tabStock Ledger Entry`.valuation_rate)
#     from `tabStock Ledger Entry`
#     where `tabStock Ledger Entry`.item_code = dni.item_code and 
# 		`tabStock Ledger Entry`.warehouse=dni.warehouse and 
# 		`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and 
# 		`tabStock Ledger Entry`.voucher_no = IF(dn.update_stock=0, dni.delivery_note, dni.parent)
# 		GROUP BY `tabStock Ledger Entry`.item_code limit 1)*SUM(dni.stock_qty), 0.0)/SUM(dni.base_amount), 2) as 'Gross Profit Percentage'
    
#     from `tabSales Invoice` si
#     inner join `tabSales Invoice Item` sii on dn.name = dni.parent
#     where dn.docstatus=1 and dn.posting_date BETWEEN %(from_date)s AND %(to_date)s GROUP BY dni.item_code