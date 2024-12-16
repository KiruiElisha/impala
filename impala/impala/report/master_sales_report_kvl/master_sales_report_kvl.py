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
			SELECT si.posting_date, si.posting_time, si.is_pos, si.is_return, si.local_and_international, si.name,
			si.cost_center, si.department, si.territory, si.lisec_inv_no, si.from_lisec, si.po_no, si.po_date, si.customer_name,
			si.customer_group, si.tax_type,
			(SELECT item_group from `tabItem` where `tabItem`.item_code = sii.item_code) as item_group,
			sii.item_code, sii.item_name, sii.posa_delivery_date, sii.withholding_tax_percentage,
			sii.withholding_tax_amount, sii.withholding_vat_percentage, sii.qty, sii.stock_uom, sii.conversion_factor,
			sii.price_list_rate, sii.base_rate, sii.base_amount, sii.rate, sii.amount, sii.base_net_amount, sii.net_amount,
			(sii.base_amount*sii.total_tax_percentage/100) as total_tax_amount,
			
			IFNULL((select `tabStock Ledger Entry`.valuation_rate from `tabStock Ledger Entry` where `tabStock Ledger Entry`.item_code = sii.item_code and 
			`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and 
			`tabStock Ledger Entry`.warehouse = sii.warehouse and
			`tabStock Ledger Entry`.voucher_no = IFNULL(IF(si.is_return, sii.parent, IF(si.update_stock=0, sii.delivery_note, sii.parent)),
			(SELECT `tabDelivery Note Item`.parent from `tabDelivery Note Item` where sii.sales_order=`tabDelivery Note Item`.against_sales_order LIMIT 1))
			limit 1)*IFNULL(sii.stock_qty,0.0),0.0) as item_cost,
			
			(sii.base_net_amount - IFNULL((select `tabStock Ledger Entry`.valuation_rate from `tabStock Ledger Entry` where `tabStock Ledger Entry`.item_code = sii.item_code and 
			`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and 
			`tabStock Ledger Entry`.warehouse = sii.warehouse and
			`tabStock Ledger Entry`.voucher_no = IFNULL(IF(si.is_return, IF(si.update_stock=0, sii.delivery_note, sii.parent), sii.parent),
				(SELECT `tabDelivery Note Item`.parent from `tabDelivery Note Item` where sii.sales_order=`tabDelivery Note Item`.against_sales_order LIMIT 1))
				 limit 1)*IFNULL(sii.stock_qty,0.0), 0.0)) as gross_profit,


			ROUND(
					(		
						IFNULL(sii.base_net_amount, 0.0) -  
						IFNULL((select `tabStock Ledger Entry`.valuation_rate from `tabStock Ledger Entry` where `tabStock Ledger Entry`.item_code = sii.item_code and 
						`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and 
						`tabStock Ledger Entry`.warehouse = sii.warehouse and
						`tabStock Ledger Entry`.voucher_no = IFNULL(IF(si.is_return, IF(si.update_stock=0, sii.delivery_note, sii.parent), sii.parent),
						 (SELECT `tabDelivery Note Item`.parent from `tabDelivery Note Item` where sii.sales_order=`tabDelivery Note Item`.against_sales_order LIMIT 1))
						 limit 1)*IFNULL(sii.stock_qty,0.0),0.0)
					)*100/IFNULL(sii.base_net_amount, 1.0)
				,2) as gp_percent


			from `tabSales Invoice` as si inner join `tabSales Invoice Item` as sii on si.name = sii.parent 
			where si.docstatus=1 {}
		""".format(conditions), as_dict=True, debug=False)
	
	return data


def get_columns():
	columns = [
		{
			"fieldname": "posting_date",
			"label":  _("Date"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 100,
		},
		{
			"fieldname": "name",
			"label":  _("Voucher No"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 100,
		},
		{
			"fieldname": "customer_name",
			"label":  _("Customer"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "customer_group",
			"label":  _("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group",
			"width": 150,
		},
		{
			"fieldname": "local_and_international",
			"label":  _("Local/International"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "item_code",
			"label":  _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},
		{
			"fieldname": "item_name",
			"label":  _("Item Name"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "item_group",
			"label":  _("Item Group"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "stock_uom",
			"label":  _("Stock UOM"),
			"fieldtype": "Data",
			"width": 80
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
			"fieldname": "base_amount",
			"label":  _("Amount"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "base_net_amount",
			"label":  _("Net Amount"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "tax_type",
			"label":  _("Tax Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "total_tax_amount",
			"label":  _("Total Tax Amount"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "withholding_tax_amount",
			"label":  _("WTH Tax Amount"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "withholding_vat_percentage",
			"label":  _("WTH %"),
			"fieldtype": "Percentage",
			"width": 100
		},
		{
			"fieldname": "item_cost",
			"label":  _("Item Cost"),
			"fieldtype": "Currency",
			"width": 100
		},	
		{
			"fieldname": "gross_profit",
			"label":  _("Gross Profit"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "gp_percent",
			"label":  _("Gross Profit %"),
			"fieldtype": "Percentage",
			"width": 100
		},

        {
            "fieldname": "cost_center",
            "label": _("Division"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 100,
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 100,
        },
        {
            "fieldname": "territory",
            "label": _("Territory"),
            "fieldtype": "Link",
            "options": "Territory",
            "width": 100,
        },

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














# SELECT
#     sii.item_name as 'Item',
#     ROUND(SUM(sii.qty), 2) AS Quantity,
#     ROUND(SUM(sii.base_amount), 2) AS 'Exclusive Amount', SUM(sii.base_net_amount) AS 'Inclusive Amount',
#     ROUND(IFNULL((select 
#             SUM(`tabStock Ledger Entry`.valuation_rate) from `tabStock Ledger Entry`
#             where `tabStock Ledger Entry`.item_code = sii.item_code and 
# 			`tabStock Ledger Entry`.warehouse=sii.warehouse and 
# 			`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and 
# 			`tabStock Ledger Entry`.voucher_no = IF(si.update_stock=0, sii.delivery_note, sii.parent)
# 			GROUP BY `tabStock Ledger Entry`.item_code limit 1)*SUM(sii.stock_qty), 0.0), 2) as 'Item Cost',
			
# 	ROUND(IFNULL(sii.base_amount - (select 
#             SUM(`tabStock Ledger Entry`.valuation_rate) from `tabStock Ledger Entry`
#             where `tabStock Ledger Entry`.item_code = sii.item_code and 
# 			`tabStock Ledger Entry`.warehouse=sii.warehouse and 
# 			`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and 
# 			`tabStock Ledger Entry`.voucher_no = IF(si.update_stock=0, sii.delivery_note, sii.parent)
# 			GROUP BY `tabStock Ledger Entry`.item_code limit 1)*SUM(sii.stock_qty), 0.0), 2) as 'Gross Profit',
    
#     ROUND(IFNULL(SUM(sii.base_amount) - (select SUM(`tabStock Ledger Entry`.valuation_rate)
#     from `tabStock Ledger Entry`
#     where `tabStock Ledger Entry`.item_code = sii.item_code and 
# 		`tabStock Ledger Entry`.warehouse=sii.warehouse and 
# 		`tabStock Ledger Entry`.voucher_type IN ('Delivery Note', 'Sales Invoice') and 
# 		`tabStock Ledger Entry`.voucher_no = IF(si.update_stock=0, sii.delivery_note, sii.parent)
# 		GROUP BY `tabStock Ledger Entry`.item_code limit 1)*SUM(sii.stock_qty), 0.0)/SUM(sii.base_amount), 2) as 'Gross Profit Percentage'
    
#     from `tabSales Invoice` si
#     inner join `tabSales Invoice Item` sii on si.name = sii.parent
#     where si.docstatus=1 and si.posting_date BETWEEN %(from_date)s AND %(to_date)s GROUP BY sii.item_code