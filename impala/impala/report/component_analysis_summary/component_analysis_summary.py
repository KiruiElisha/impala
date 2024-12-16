# Copyright (c) 2024, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns, data = get_columns(), []

    # Construct conditions for filtering
    conditions = " WHERE so.docstatus = 1"
    if filters.get('from_date'):
        conditions += " AND so.creation >= %(from_date)s"
    if filters.get('to_date'):
        conditions += " AND so.creation <= %(to_date)s"
    if filters.get('status'):
        conditions += " AND so.status = %(status)s"
    if filters.get('name'):
        conditions += " AND so.name = %(name)s"
    if filters.get('item_code'):
        conditions += " AND soic.item_code = %(item_code)s"
    
    sales_orders = frappe.db.sql(f"""
        SELECT 
            so.name AS sales_order,
            soic.item_code,
            soic.price_type,
            soi.delivered_qty,
            soi.delivered_pcs,
            soic.qty
        FROM 
            `tabSales Order` so
        JOIN 
            `tabSales Order Item` soi ON soi.parent = so.name
        JOIN 
            `tabSales Order Item Components` soic ON soic.item_detail = soi.name
        JOIN 
            `tabItem` item ON item.name = soic.item_code
        {conditions}
        AND item.is_stock_item = 0
        ORDER BY
            so.name, soic.item_code
    """, filters, as_dict=True)
    
    service_qty_map = {}

    # Debugging: Print the retrieved sales orders
    frappe.logger().debug(f"Retrieved sales orders: {sales_orders}")
    
    for order in sales_orders:
        key = (order.sales_order, order.item_code)
        if order.price_type == 'SQM Pricing':
            service_qty = order.qty * order.delivered_qty
        else:
            service_qty = order.qty * order.delivered_pcs

        if key not in service_qty_map:
            service_qty_map[key] = 0
        service_qty_map[key] += service_qty
    
    for (sales_order, item_code), total_service_qty in service_qty_map.items():
        data.append({
            'sales_order': sales_order,
            'item_code': item_code,
            'total_service_qty': total_service_qty,
        })
    
    return columns, data

def get_columns():
    return [
        {
            'fieldname': 'sales_order',
            'fieldtype': 'Link',
            'label': _('Sales Order'),
            'options': 'Sales Order',
            'width': 180,
        },
        {
            'fieldname': 'item_code',
            'fieldtype': 'Link',
            'label': _('Item Code'),
            'options': 'Item',
            'width': 120,
        },
        {
            'fieldname': 'total_service_qty',
            'fieldtype': 'Float',
            'label': _('Total Service Quantity'),
            'width': 150,
        }
    ]


