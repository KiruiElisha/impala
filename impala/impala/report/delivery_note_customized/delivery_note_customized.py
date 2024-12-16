

import frappe

def execute(filters=None):
    columns = [
        {"label": "Delivery Note", "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 150},
        {"label": "Sales Order", "fieldname": "against_sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 150},
        {"label": "Delivery Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 150},
        {"label": "Customer PO", "fieldname": "po_no", "fieldtype": "Data", "width": 150},
        {"label": "Sales Person", "fieldname": "customer_full_name", "fieldtype": "Link", "options": "Sales Person", "width": 150},
        {"label": "Lisec Order Id", "fieldname": "lisec_order_id", "fieldtype": "Data","width": 150},
        {"label": "Total PCs", "fieldname": "total_pcs", "fieldtype": "Int", "width": 100},
        {"label": "Total Quantity", "fieldname": "total_quantity", "fieldtype": "Float", "width": 100},
        {"label": "Total Weight", "fieldname": "total_net_weight", "fieldtype": "Float", "width": 100},
        {"label": "Currency", "fieldname": "currency", "fieldtype": "Data", "width": 20},
        {"label": "Total Price", "fieldname": "total_price", "fieldtype": "Data", "width": 100},
    ]

    data = fetch_data(filters)
    return columns, data

def fetch_data(filters):
    conditions = []
    delivery_note_number = filters.get("delivery_note_number")
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    against_sales_order = filters.get("against_sales_order")

    if delivery_note_number:
        conditions.append(f"dn.name = '{delivery_note_number}'")
    if from_date:
        conditions.append(f"dn.posting_date >= '{from_date}'")
    if to_date:
        conditions.append(f"dn.posting_date <= '{to_date}'")
    if against_sales_order:
        conditions.append(f"dni.against_sales_order = '{against_sales_order}'")

    conditions_str = " AND ".join(conditions) if conditions else "1=1"

    sql_query = f"""
        SELECT
            dn.name AS delivery_note,
            dn.posting_date,
            dni.against_sales_order,
            dn.sales_order_id,
            dn.po_no,
            dn.customer,
            tc.customer_name AS customer_full_name,
            dn.total_net_weight,
            dn.currency,
            SUM(dni.pcs) AS total_pcs,
            SUM(dni.qty) AS total_quantity,
            SUM(dni.amount) AS total_price,   
            tmr.sales_order_id AS material_request_sales_order_id,
            tmr.lisec_order_id
        FROM
            `tabDelivery Note` AS dn
        LEFT JOIN
            `tabDelivery Note Item` AS dni ON dn.name = dni.parent
        LEFT JOIN
            `tabMaterial Request` AS tmr ON dn.sales_order_id = tmr.sales_order_id
        LEFT JOIN
            `tabCustomer` AS tc ON dn.customer = tc.name
        WHERE
            {conditions_str}
        GROUP BY
            dn.name
    """

    data = frappe.db.sql(sql_query, as_dict=True)
    return data
