# Copyright (c) 2024, Codes Soft and contributors
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
    conditions = get_conditions(filters)
    group_table = filters.groupby
    group_list = []
    
    # Fetching group list based on group_table
    if group_table not in ('Item Group', 'Warehouse'):
        group_list = frappe.db.get_list(group_table, {'company': filters.company}, ['name', frappe.scrub(group_table) + '_name'])
    else:
        group_list = frappe.db.get_list(group_table, {'company': filters.company}, pluck='name')

    # Initialize totals
    totals = {'description': '<b>Totals</b>', 'qty': 0.0, 'base_net_amount': 0.0, 'item_cost': 0.0, 'gross_profit': 0.0, 'gp_percent': 0.0}
    
    for group in group_list:
        # Group totals setup
        group_totals = {'description': f"<b>{group[frappe.scrub(group_table)+'_name']} Totals</b>" if group_table not in ('Item Group', 'Warehouse') else f"<b>{group} Totals</b>",
                        'qty': 0.0, 'base_net_amount': 0.0, 'item_cost': 0.0, 'gross_profit': 0.0, 'gp_percent': 0.0}
        
        # Get data per group
        child_query = get_data(filters, conditions, group['name']) if group_table not in ('Item Group', 'Warehouse') else get_data(filters, conditions, group)

        if child_query:
            # Append group header
            data.append({'item_code': f"<b>{group[frappe.scrub(group_table)+'_name']}</b>" if group_table not in ('Item Group', 'Warehouse') else f"<b>{group}</b>"})
            
            for d in child_query:
                # Calculate gross profit percentage
                d['gp_percent'] = round(((d.get("base_net_amount") or 0.0) - (d.get("item_cost") or 0.0)) * 100 / (d.get("base_net_amount") or 1.0), 2)
                
                # Accumulate group totals
                group_totals['qty'] += d.get("qty")
                group_totals['base_net_amount'] += d.get("base_net_amount")
                group_totals['item_cost'] += d.get("item_cost")
                group_totals['gross_profit'] += d.get("gross_profit")

                # Accumulate overall totals
                totals['qty'] += d.get("qty")
                totals['base_net_amount'] += d.get("base_net_amount")
                totals['item_cost'] += d.get("item_cost")
                totals['gross_profit'] += d.get("gross_profit")

            # Calculate group profit percentage
            group_totals['gp_percent'] = round((group_totals['gross_profit'] / (group_totals['base_net_amount'] or 1.0)) * 100, 2)
            data.extend(child_query)
            data.append(group_totals)

    # Calculate overall profit percentage and append totals
    totals["gp_percent"] += round((totals['gross_profit'] / (totals['base_net_amount'] or 1.0)) * 100, 2)
    data.append(totals)

    return columns, data


def get_columns():
    # Define column structure and widths
    columns = [
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Data",
            "options": "Item",
            "width": 250  # Set a reasonable width for Item Code
        },
        {
            "fieldname": "description",
            "label": _("Item Description"),
            "fieldtype": "Data",
            "width": 350  # Set a reasonable width for Description
        },
        {
            "fieldname": "voucher_no",
            "label": _("Voucher No"),
            "fieldtype": "Link",
            "options": "Delivery Note",
            "width": 150
        },
        {
            "fieldname": "qty",
            "label": _("Quantity"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "base_net_amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "item_cost",
            "label": _("Item Cost"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "gross_profit",
            "label": _("Profit"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "gp_percent",
            "label": _("Profit %"),
            "fieldtype": "Percentage",
            "width": 150
        }
    ]

    return columns



def get_data(filters, conditions, group):
    group_by_field = "si." + frappe.scrub(filters.groupby) if filters.groupby not in ('Item Group', 'Warehouse') else "sii." + frappe.scrub(filters.groupby)
    data = frappe.db.sql(f"""
        SELECT 
            si.name as voucher_no, 
            CONCAT("<span style='margin-left: 20px'>", sii.item_code, "</span>") as item_code, 
            CONCAT(sii.item_code, ' ', sii.item_name) as item_name, 
            sii.description, 
            CONCAT(si.customer, ' ', si.customer_name) as customer,
            si.territory, 
            cu.customer_group, 
            sii.qty, 
            sii.base_amount, 
            sii.base_net_amount, 
            sii.warehouse,
            COALESCE(
                (SELECT `tabStock Ledger Entry`.valuation_rate 
                 FROM `tabStock Ledger Entry` 
                 WHERE `tabStock Ledger Entry`.item_code = sii.item_code 
                   AND `tabStock Ledger Entry`.voucher_type IN ('Delivery Note') 
                   AND `tabStock Ledger Entry`.warehouse = sii.warehouse 
                   AND `tabStock Ledger Entry`.voucher_no = sii.parent 
                   AND `tabStock Ledger Entry`.item_code = sii.item_code 
                 LIMIT 1) * COALESCE(sii.stock_qty, 0.0), 
                0.0) AS item_cost,
            (sii.base_net_amount - COALESCE(
                (SELECT `tabStock Ledger Entry`.valuation_rate 
                 FROM `tabStock Ledger Entry` 
                 WHERE `tabStock Ledger Entry`.item_code = sii.item_code 
                   AND `tabStock Ledger Entry`.voucher_type IN ('Delivery Note') 
                   AND `tabStock Ledger Entry`.warehouse = sii.warehouse 
                   AND `tabStock Ledger Entry`.voucher_no = sii.parent 
                   AND `tabStock Ledger Entry`.item_code = sii.item_code 
                 LIMIT 1) * COALESCE(sii.stock_qty, 0.0), 
                0.0)) AS gross_profit
        FROM `tabDelivery Note` AS si 
        INNER JOIN `tabDelivery Note Item` AS sii ON si.name = sii.parent
        INNER JOIN `tabCustomer` AS cu ON si.customer = cu.name
        LEFT JOIN `tabSales Team` AS st ON si.name = st.parent
        WHERE si.docstatus=1 AND si.status = 'Closed' AND {group_by_field} = %s {conditions}
    """, (group,), as_dict=True, debug=False)

    return data


# def get_columns():
#     columns = [
#         {
# 			"fieldname": "item_code",
# 			"label":  _("Item Code"),
# 			"fieldtype": "Data",
# 			"options": "Item",
# 			"width": 250
# 		},
# 		{
# 			"fieldname": "description",
# 			"label":  _("Item Description"),
# 			"fieldtype": "Data",
# 			"width": 350,
# 		},
# 		{
# 			"fieldname": "voucher_no",
# 			"label":  _("Voucher No"),
# 			"fieldtype": "Link",
# 			"options": "Delivery Note",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "qty",
# 			"label":  _("Quantity"),
# 			"fieldtype": "Float",
# 			"width": 100
# 		},
# 		{
# 			"fieldname": "base_net_amount",
# 			"label":  _("Amount"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "item_cost",
# 			"label":  _("Item Cost"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},	
# 		{
# 			"fieldname": "gross_profit",
# 			"label":  _("Profit"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "gp_percent",
# 			"label":  _("Profit %"),
# 			"fieldtype": "Percentage",
# 			"width": 150
# 		},
		
#     ]

#     return columns

def get_conditions(filters):
    conditions = ""
    if filters.company:
        conditions += " AND si.company = '{}'".format(filters.company)
    if filters.from_date and filters.to_date:
        conditions += " AND si.posting_date BETWEEN '{}' AND '{}'".format(filters.from_date, filters.to_date)
    if filters.voucher_no:
        voucher_nos = tuple(filters.voucher_no)
        conditions += " AND si.name IN {}".format(voucher_nos)
    if filters.item_code:
        items = tuple(filters.item_code)
        conditions += " AND sii.item_code IN {}".format(items)
    if filters.cost_center:
        cost_centers = tuple(filters.cost_center)
        conditions += " AND si.cost_center IN {}".format(cost_centers)
    if filters.department:
        departments = tuple(filters.department)
        conditions += " AND si.department IN {}".format(departments)
    if filters.customer:
        customers = tuple(filters.customer)
        conditions += " AND si.customer IN {}".format(customers)
    if filters.sales_person:
        sales_person = tuple(filters.sales_person)
        conditions += " AND st.sales_person IN {}".format(sales_person)
    if filters.customer_group:
        customer_groups = tuple(filters.customer_group)
        conditions += " AND cu.customer_group IN {}".format(customer_groups)
    if filters.territory:
        territories = tuple(filters.territory)
        conditions += " AND si.territory IN {}".format(territories)
    if filters.warehouse:
        warehouses = tuple(filters.warehouse)
        conditions += " AND sii.warehouse IN {}".format(warehouses)
    return conditions
