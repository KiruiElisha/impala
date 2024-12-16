import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = list(get_data_generator(filters))
    return columns, data

def get_columns():
    return [
         {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
          {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 150},
        {"label": _("Delivery Note"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 150},       
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 150},
        {"label": _("Delivered Qty"), "fieldname": "delivered_qty", "fieldtype": "Float", "width": 150},
        {"label": _("Balance Qty"), "fieldname": "balance_qty", "fieldtype": "Float", "width": 150},
        {"label": _("Delivery Date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 150},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 150},
    ]

def get_data_generator(filters):
    conditions = get_conditions(filters)
    
    query = """
        SELECT
            dn.name as delivery_note,
            dn.customer,
            dni.against_sales_order as sales_order,
            so.total_qty,
            SUM(dni.qty) as delivered_qty,
            dn.posting_date as delivery_date,
            dn.status
        FROM
            `tabDelivery Note` dn
        JOIN
            `tabDelivery Note Item` dni ON dn.name = dni.parent
        LEFT JOIN
            `tabSales Order` so ON dni.against_sales_order = so.name
        WHERE
            dn.docstatus = 1
            {conditions}
        GROUP BY
            dn.name, dni.against_sales_order
        ORDER BY
            dn.posting_date DESC
    """.format(conditions=conditions)

    for row in frappe.db.sql(query, filters, as_dict=1):
        row['balance_qty'] = row['total_qty'] - row['delivered_qty'] if row['total_qty'] else 0
        yield row

def get_conditions(filters):
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("dn.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("dn.posting_date <= %(to_date)s")
    if filters.get("customer"):
        conditions.append("dn.customer = %(customer)s")
    if filters.get("sales_order"):
        conditions.append("dni.against_sales_order = %(sales_order)s")

    return "AND " + " AND ".join(conditions) if conditions else ""