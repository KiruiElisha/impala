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
import operator

def execute(filters=None):
    if not filters:
        filters = {}

    columns, data = get_columns(), []
    conditions = get_conditions(filters)
    group_table = filters.groupby
    group_list = []
    if group_table not in ('Item Group', 'Warehouse'):
        group_list = frappe.db.get_list(group_table, {'company': filters.company}, ['name', frappe.scrub(group_table) + '_name'])
    else:
        group_list = frappe.db.get_list(group_table, {'company': filters.company}, pluck='name')
    totals = {'description': '<b>Totals</b>', 'qty': 0.0, 'base_net_amount': 0.0, 'item_cost': 0.0, 'gross_profit': 0.0, 'gp_percent': 0.0}

    for group in group_list:
        group_totals = {'description': "<b>" + group[frappe.scrub(group_table) + '_name'] + ' Totals' + "</b>", 'qty': 0.0, 'base_net_amount': 0.0, 'item_cost': 0.0, 'gross_profit': 0.0, 'gp_percent': 0.0} \
            if group_table not in ('Item Group', 'Warehouse') else {'description': "<b>" + group + ' Totals' + "</b>", 'qty': 0.0, 'base_net_amount': 0.0, 'item_cost': 0.0, 'gross_profit': 0.0, 'gp_percent': 0.0}
        child_query = get_data(filters, conditions, group['name']) if group_table not in ('Item Group', 'Warehouse') else get_data(filters, conditions, group)
        if child_query:
            if group_table not in ('Item Group', 'Warehouse'):
                data.append({'item_code': "<b>" + group[frappe.scrub(group_table) + '_name'] + "</b>"})
            else:
                data.append({'item_code': "<b>" + group + "</b>"})

            child_obj = child_query
            for d in child_obj:
                d['gp_percent'] = round(((d.get("base_net_amount") or 0.0) - (d.get("item_cost") or 0.0)) * 100 / (d.get("base_net_amount") or 1.0), 2)
                group_totals['qty'] += d.get("qty")
                group_totals['base_net_amount'] += d.get("base_net_amount")
                group_totals['item_cost'] += d.get("item_cost")
                group_totals['gross_profit'] += d.get("gross_profit")
                totals['qty'] += d.get("qty")
                totals['base_net_amount'] += d.get("base_net_amount")
                totals['item_cost'] += d.get("item_cost")
                totals['gross_profit'] += d.get("gross_profit")
            group_totals['gp_percent'] = round((group_totals.get("gross_profit") / (group_totals.get("base_net_amount") if group_totals.get("base_net_amount") != 0.0 else 1.0)) * 100, 2)
            data.extend(child_obj)
            data.append(group_totals)
    totals["gp_percent"] = round((totals.get("gross_profit") / (totals.get("base_net_amount") if totals.get("base_net_amount") != 0.0 else 1.0)) * 100, 2)
    data.append(totals)
    return columns, data

def get_data(filters, conditions, group):
    try:
        group_field = "si." + frappe.scrub(filters.groupby) if filters.groupby not in ('Item Group', 'Warehouse') else "sii." + frappe.scrub(filters.groupby)
        
        query = """
        SELECT 
            si.name AS voucher_no,
            CONCAT('<span style="margin-left: 20px">', sii.item_code, '</span>') AS item_code,
            sii.description,
            sii.qty,
            sii.base_net_amount,
            item.item_category,
            item.item_group,
            st.sales_person,
            COALESCE(
                (SELECT valuation_rate 
                 FROM `tabStock Ledger Entry` sle
                 WHERE sle.item_code = sii.item_code
                   AND sle.voucher_type IN ('Delivery Note', 'Sales Invoice')
                   AND sle.warehouse = sii.warehouse
                   AND sle.voucher_no = COALESCE(
                       IF(si.is_return = 0, IF(si.update_stock = 0, sii.delivery_note, sii.parent), sii.delivery_note),
                       (SELECT parent FROM `tabDelivery Note Item` WHERE against_sales_order = sii.sales_order LIMIT 1)
                   )
                 LIMIT 1
                ) * COALESCE(sii.stock_qty, 0), 0
            ) AS item_cost,
            (sii.base_net_amount - 
             COALESCE(
                (SELECT valuation_rate 
                 FROM `tabStock Ledger Entry` sle
                 WHERE sle.item_code = sii.item_code
                   AND sle.voucher_type IN ('Delivery Note', 'Sales Invoice')
                   AND sle.warehouse = sii.warehouse
                   AND sle.voucher_no = COALESCE(
                       IF(si.is_return = 0, IF(si.update_stock = 0, sii.delivery_note, sii.parent), sii.delivery_note),
                       (SELECT parent FROM `tabDelivery Note Item` WHERE against_sales_order = sii.sales_order LIMIT 1)
                   )
                 LIMIT 1
                ) * COALESCE(sii.stock_qty, 0), 0
             )
            ) AS gross_profit
        FROM 
            `tabSales Invoice View` AS si 
        INNER JOIN 
            `tabSales Invoice Item View` AS sii ON si.name = sii.parent 
        LEFT JOIN 
            `tabItem` AS item ON sii.item_code = item.name 
        LEFT JOIN 
            `tabSales Team` AS st ON st.parent = sii.parent
        WHERE 
            si.docstatus = 1 
            AND {group_field} = %s
            {conditions}
        """
        
        data = frappe.db.sql(query.format(group_field=group_field, conditions=conditions), 
                             values=[group], 
                             as_dict=True, 
                             debug=True)
        
        return data
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error in Inventory Sales Closed Deliveries Report")
        frappe.throw(f"An error occurred while fetching data: {str(e)}")

def get_columns():
    columns = [
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Data",
            "options": "Item",
            "width": 250
        },
        {
            "fieldname": "description",
            "label": _("Item Description"),
            "fieldtype": "Data",
            "width": 350,
        },
        {
            "fieldname": "item_group",
            "label": _("Item Group"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "voucher_no",
            "label": _("Voucher No"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
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
        },
        {
            "fieldname": "item_category",
            "label": _("Item Category"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "sales_person",
            "label": _("Sales Person"),
            "fieldtype": "Data",
            "width": 150
        },
    ]

    return columns

def get_conditions(filters):
    conditions = ""
    if filters.brand:
        conditions += "AND item.brand = '{}'".format(filters.brand)

    if filters.company:
        conditions += " and si.company = '{}'".format(filters.company)
    if filters.from_date:
        conditions += " and si.posting_date BETWEEN '{}' AND '{}'".format(filters.from_date, filters.to_date)

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

    if filters.item_category:
        item_category = filters.item_category
        if len(item_category) < 2:
            item_category.append("")
        item_category = tuple(item_category)
        conditions += " and item.item_category IN {}".format(item_category)

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
    
    if filters.item_code:
        items = filters.item_code
        if len(items) < 2:
            items.append("")
        items = tuple(items)
        conditions += " and sii.item_code IN {}".format(items)

    if filters.item_group:
        item_groups = filters.item_group
        if len(item_groups) < 2:
            item_groups.append("")
        item_groups = tuple(item_groups)
        conditions += " and sii.item_group IN {}".format(item_groups)

    if filters.customer_group:
        cstr_groups = filters.customer_group
        if len(cstr_groups) < 2:
            cstr_groups.append("")
        cstr_groups = tuple(cstr_groups)
        conditions += " and si.customer_group IN {}".format(cstr_groups)

    if filters.warehouse:
        warehouses = filters.warehouse
        if len(warehouses) < 2:
            warehouses.append("")
        warehouses = tuple(warehouses)
        conditions += " and sii.warehouse IN {}".format(warehouses)

    if filters.territory:
        territories = filters.territory
        if len(territories) < 2:
            territories.append("")
        territories = tuple(territories)
        conditions += " and si.territory IN {}".format(territories)

    return conditions
