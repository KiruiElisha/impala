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
        result_obj.setdefault(d.item_code, {'description': d.item_name, 'qty': 0.0, 'base_amount': 0.0, 'base_net_amount': 0.0, 'item_cost': 0.0, 'gross_profit': 0.0}) \
            if filters.get("group_by") == 'Item' else result_obj.setdefault(d.name, {'description': d.name, 'qty': 0.0, 'base_amount': 0.0, 'base_net_amount': 0.0, 'item_cost': 0.0, 'gross_profit': 0.0})

    for r in query:
        gkey = r.name if filters.get("group_by") == 'Voucher' else r.item_code
        result_obj[gkey]['customer'] = r.customer
        result_obj[gkey]['customer_group'] = r.customer_group
        result_obj[gkey]['territory'] = r.territory
        result_obj[gkey]['warehouse'] = r.warehouse
        result_obj[gkey]['qty'] += r.qty
        result_obj[gkey]['base_amount'] += r.base_amount
        result_obj[gkey]['base_net_amount'] += r.base_net_amount
        result_obj[gkey]['item_cost'] += r.item_cost
        result_obj[gkey]['gross_profit'] += r.gross_profit

    for key, val in result_obj.items():
        row = {}
        row['description'] = val['description']
        row['customer'] = val['customer']
        row['customer_group'] = val['customer_group']
        row['territory'] = val['territory']
        row['warehouse'] = val['warehouse']
        row['qty'] = val['qty']
        row['base_amount'] = val['base_amount']
        row['base_net_amount'] = val['base_net_amount']
        row['item_cost'] = val['item_cost']
        row['gross_profit'] = val['gross_profit']
        row['gp_percent'] = round((val['gross_profit'] * 100 / (val['base_net_amount'] if val['base_net_amount'] != 0 else 1.0)), 2)
        data.append(row)

    return columns, data

def get_data(filters, conditions):
    data = frappe.db.sql("""
        SELECT 
            si.name, sii.item_code, CONCAT(sii.item_code, ' ', sii.item_name) as item_name, sii.description, CONCAT(si.customer, ' ', si.customer_name) as customer,
            si.territory, cu.customer_group, sii.qty, sii.base_amount, sii.base_net_amount, sii.warehouse,
            IFNULL((SELECT `tabStock Ledger Entry`.valuation_rate FROM `tabStock Ledger Entry` WHERE `tabStock Ledger Entry`.item_code = sii.item_code AND 
            `tabStock Ledger Entry`.voucher_type IN ('Delivery Note') AND 
            `tabStock Ledger Entry`.warehouse = sii.warehouse AND
            `tabStock Ledger Entry`.voucher_no = sii.parent AND
            `tabStock Ledger Entry`.item_code = sii.item_code LIMIT 1)*IFNULL(sii.stock_qty,0.0),0.0) AS item_cost,
            (sii.base_net_amount - IFNULL((SELECT `tabStock Ledger Entry`.valuation_rate FROM `tabStock Ledger Entry` WHERE `tabStock Ledger Entry`.item_code = sii.item_code AND 
            `tabStock Ledger Entry`.voucher_type IN ('Delivery Note') AND 
            `tabStock Ledger Entry`.warehouse = sii.warehouse AND
            `tabStock Ledger Entry`.voucher_no = sii.parent AND
            `tabStock Ledger Entry`.item_code = sii.item_code LIMIT 1)*IFNULL(sii.stock_qty,0.0), 0.0)) AS gross_profit
        FROM `tabDelivery Note` AS si 
        INNER JOIN `tabDelivery Note Item` AS sii ON si.name = sii.parent
        INNER JOIN `tabCustomer` AS cu ON si.customer = cu.name
        LEFT JOIN `tabSales Team` AS st ON si.name = st.parent -- Join with tabSales Team Department Wise
        WHERE si.docstatus=1 AND si.status = 'Closed' {}
    """.format(conditions), as_dict=True, debug=False)

    return data

def get_columns():
    columns = [
        {
            "fieldname": "description",
            "label": _("Description"),
            "fieldtype": "Data",
            "width": 180,
            "align": "left",
        },
        {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Data",
            "width": 320,
            "align": "left",
        },
        {
            "fieldname": "customer_group",
            "label": _("Customer Group"),
            "fieldtype": "Link",
            "options": "Customer Group",
            "width": 200,
            "align": "left",
        },
        {
            "fieldname": "territory",
            "label": _("Territory"),
            "fieldtype": "Link",
            "options": "Territory",
            "width": 200,
            "align": "left",
        },
        {
            "fieldname": "warehouse",
            "label": _("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 200,
            "align": "left",
        },
        {
            "fieldname": "qty",
            "label": _("Qty"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "base_amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "fieldname": "base_net_amount",
            "label": _("Net Amount"),
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "fieldname": "item_cost",
            "label": _("Item Cost"),
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "fieldname": "gross_profit",
            "label": _("Gross Profit"),
            "fieldtype": "Currency",
            "width": 160
        },
        {
            "fieldname": "gp_percent",
            "label": _("Gross Profit %"),
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
        if len(voucher_nos) < 2:
            voucher_nos.append("")
        voucher_nos = tuple(voucher_nos)
        conditions += " and si.name IN {}".format(voucher_nos)

    if filters.item_code:
        items = filters.item_code
        if len(items) < 2:
            items.append("")
        items = tuple(items)
        conditions += " and sii.item_code IN {}".format(items)

    if filters.cost_center:
        cost_centers = filters.cost_center
        if len(cost_centers) < 2:
            cost_centers.append("")
        cost_centers = tuple(cost_centers)
        conditions += "and si.cost_center IN {}".format(cost_centers)

    if filters.department:
        departments = filters.department
        if len(departments) < 2:
            departments.append("")
        departments = tuple(departments)
        conditions += " and si.department IN {}".format(departments)

    if filters.customer:
        customers = filters.customer
        if len(customers) < 2:
            customers.append("")
        customers = tuple(customers)
        conditions += " and si.customer IN {}".format(customers)

    if filters.sales_person:
        sales_person = filters.sales_person
        if len(sales_person) < 2:
            sales_person.append("")
        sales_person = tuple(sales_person)
        conditions += " and st.sales_person IN {}".format(sales_person)

    if filters.customer_group:
        customer_groups = filters.customer_group
        if len(customer_groups) < 2:
            customer_groups.append("")
        customer_groups = tuple(customer_groups)
        conditions += " and cu.customer_group IN {}".format(customer_groups)

    if filters.territory:
        territories = filters.territory
        if len(territories) < 2:
            territories.append("")
        territories = tuple(territories)
        conditions += " and si.territory IN {}".format(territories)
    
    if filters.warehouse:
        warehouses = filters.warehouse
        if len(warehouses) < 2:
            warehouses.append("")
        warehouses = tuple(warehouses)
        conditions += " and sii.warehouse IN {}".format(warehouses)
    
    return conditions
