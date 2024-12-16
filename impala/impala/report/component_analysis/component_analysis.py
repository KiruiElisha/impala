import frappe
from frappe import _

def execute(filters=None):
    columns, data = get_columns(), []

    # Construct conditions for filtering
    conditions = ["so.docstatus = 1"]
    if filters.get('from_date'):
        conditions.append("so.creation >= %(from_date)s")
    if filters.get('to_date'):
        conditions.append("so.creation <= %(to_date)s")
    if filters.get('status'):
        conditions.append("so.status = %(status)s")
    if filters.get('name'):
        conditions.append("so.name = %(name)s")
    if filters.get('item_code'):
        conditions.append("soic.item_code = %(item_code)s")
    
    conditions_str = " AND ".join(conditions)
    
    # Fetch data from Sales Order and its child tables, and filter items based on is_stock_item
    sales_orders = frappe.db.sql(f"""
        SELECT 
            so.name AS sales_order,
            soi.name AS sales_order_item,
            soi.delivered_qty,
            soic.item_code,
            soic.item_name,
            soic.item_group,
            soic.price_type,
            soic.unit,
            soic.qty,
            soic.price,
            soic.item_total_amount,
            soic.wastage_per,
            soic.wastage_qty,
            soic.wastage_price,
            soic.wastage_total_amount,
            soic.final_item_price,
            soic.item_detail
        FROM 
            `tabSales Order` so
        JOIN 
            `tabSales Order Item` soi ON soi.parent = so.name
        JOIN 
            `tabSales Order Item Components` soic ON soic.item_detail = soi.name
        JOIN 
            `tabItem` item ON item.name = soic.item_code
        WHERE
            {conditions_str} AND item.is_stock_item = 0
        ORDER BY
            so.name
    """, filters, as_dict=True)
    
    # Process the fetched data
    for order in sales_orders:
        if order.price_type == 'SQM Pricing':
            service_qty = order.qty * order.delivered_qty
        else:
            service_qty = order.qty
        
        data.append({
            'sales_order': order.sales_order,
            'sales_order_item': order.sales_order_item,
            'delivered_qty': order.delivered_qty,
            'delivered_pcs': 0.0,
            'item_code': order.item_code,
            'item_name': order.item_name,
            'item_group': order.item_group,
            'price_type': order.price_type,
            'unit': order.unit,
            'qty': order.qty,
            'price': order.price,
            'item_total_amount': order.item_total_amount,
            'wastage_per': order.wastage_per,
            'wastage_qty': order.wastage_qty,
            'wastage_price': order.wastage_price,
            'wastage_total_amount': order.wastage_total_amount,
            'final_item_price': order.final_item_price,
            'item_detail': order.item_detail,
            'service_qty': service_qty
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
            'fieldname': 'item_name',
            'fieldtype': 'Data',
            'label': _('Item Name'),
            'width': 150,
        },
        {
            'fieldname': 'item_group',
            'fieldtype': 'Link',
            'label': _('Item Group'),
            'options': 'Item Group',
            'width': 120,
        },
        {
            'fieldname': 'price_type',
            'fieldtype': 'Data',
            'label': _('Price Type'),
            'width': 120,
        },
        {
            'fieldname': 'unit',
            'fieldtype': 'Data',
            'label': _('Unit'),
            'width': 100,
        },
        {
            'fieldname': 'qty',
            'fieldtype': 'Float',
            'label': _('Qty'),
            'width': 100,
        },
        {
            'fieldname': 'price',
            'fieldtype': 'Currency',
            'label': _('Price'),
            'width': 120,
        },
        {
            'fieldname': 'item_total_amount',
            'fieldtype': 'Currency',
            'label': _('Item Total Amount'),
            'width': 150,
        },
        {
            'fieldname': 'wastage_per',
            'fieldtype': 'Percent',
            'label': _('Wastage %'),
            'width': 100,
        },
        {
            'fieldname': 'wastage_qty',
            'fieldtype': 'Float',
            'label': _('Wastage Qty'),
            'width': 120,
        },
        {
            'fieldname': 'wastage_price',
            'fieldtype': 'Currency',
            'label': _('Wastage Price'),
            'width': 120,
        },
        {
            'fieldname': 'wastage_total_amount',
            'fieldtype': 'Currency',
            'label': _('Wastage Total Amount'),
            'width': 150,
        },
        {
            'fieldname': 'final_item_price',
            'fieldtype': 'Currency',
            'label': _('Final Item Price'),
            'width': 150,
        },
        {
            'fieldname': 'delivered_qty',
            'fieldtype': 'Float',
            'label': _('Delivered Qty'),
            'width': 120,
        },
        {
            'fieldname': 'delivered_pcs',
            'fieldtype': 'Float',
            'label': _('Delivered Pcs'),
            'width': 120,
        },
        {
            'fieldname': 'service_qty',
            'fieldtype': 'Float',
            'label': _('Service Qty'),
            'width': 150,
        }
    ]
