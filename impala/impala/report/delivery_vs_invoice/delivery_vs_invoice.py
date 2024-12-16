import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = list(get_data_generator(filters))
    return columns, data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": _("Delivery Note"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 150},
        {"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150}, 
        {"label": _("Curreny"), "fieldname": "currency", "fieldtype": "Data", "width": 150},      
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 150},
        {"label": _("Invoiced Qty"), "fieldname": "qty_invoiced", "fieldtype": "Float", "width": 150},
        {"label": _("Balance Qty"), "fieldname": "balance_qty", "fieldtype": "Float", "width": 150},
        {"label": _("Delivery Date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 150},
        {"label": _("Delivery Amount"), "fieldname": "delivery_amount", "fieldtype": "Data", "width": 150},
        {"label": _("Invoice Date"), "fieldname": "invoiced_date", "fieldtype": "Date", "width": 150},
        {"label": _("Invoice Amount"), "fieldname": "invoiced_amount", "fieldtype": "Data", "width": 150},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 150},
    ]

def get_data_generator(filters):
    conditions = get_conditions(filters)
    
    query = """
        SELECT
            so.customer,
            so.customer_name,
            so.name as delivery_note,
            so.total as delivery_amount,
            so.posting_date as delivery_date,
            dn.total as invoiced_amount,
            dn.name as sales_invoice,
            so.total_qty,
            SUM(dni.qty) as qty_invoiced,
            dn.posting_date as invoiced_date,
            dn.status,
            so.currency
        FROM
            `tabDelivery Note` so
        LEFT JOIN
            `tabSales Invoice Item` dni ON dni.delivery_note = so.name
        LEFT JOIN
            `tabSales Invoice` dn ON dni.parent = dn.name
        LEFT JOIN
            `tabCustomer` c ON so.customer=dn.name
        WHERE
            so.docstatus = 1
            {conditions}
        GROUP BY
            so.name, dn.name
        ORDER BY
            dn.posting_date DESC, so.name
    """.format(conditions=conditions)

    for row in frappe.db.sql(query, filters, as_dict=1):
        total_qty = row['total_qty'] or 0
        qty_invoiced = row['qty_invoiced'] or 0
        row['balance_qty'] = total_qty - qty_invoiced
        
        # Apply the filter to remove rows with zero balance quantity
        if filters.get("remove_zero_balance") and row['balance_qty'] == 0:
            continue
        
        yield row

def get_conditions(filters):
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("so.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("so.posting_date <= %(to_date)s")
    if filters.get("customer"):
        conditions.append("so.customer = %(customer)s")
    if filters.get("delivery_note"):
        conditions.append("so.name = %(delivery_note)s")
    if filters.get("warehouse"):
        conditions.append("dni.warehouse = %(warehouse)s")
    if filters.get("cost_center"):
        conditions.append("dn.cost_center = %(cost_center)s")
    if filters.get("customer_group"):
        conditions.append("c.customer_group = %(customer_group)s")
    if filters.get("department"):
        conditions.append("dn.department = %(department)s")
    if filters.get("status"):
        conditions.append("dn.status = %(status)s")

    return "AND " + " AND ".join(conditions) if conditions else ""
