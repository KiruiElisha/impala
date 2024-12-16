import frappe
from frappe import _
from frappe.utils import cstr
import json

def execute(filters=None):
    if not filters:
        filters = {}

    columns, data = get_columns(), []
    conditions = get_conditions(filters)
    group_table = filters.groupby
    totals = {
        'description': '<b>Totals</b>', 
        'qty': 0.0, 
        'base_net_amount': 0.0, 
        'item_cost': 0.0, 
        'gross_profit': 0.0, 
        'gp_percent': 0.0
    }

    group_list = frappe.db.get_list(group_table, {'company': filters.company}, pluck='name')

    all_data = get_all_data(filters, conditions, group_list)

    for group in group_list:
        group_data = [d for d in all_data if d[frappe.scrub(group_table)] == group]
        if group_data:
            group_totals = calculate_totals(group_data)
            group_totals['description'] = f"<b>{group} Totals</b>"
            totals = update_totals(totals, group_totals)
            data.append({'item_code': f"<b>{group}</b>"})
            data.extend(group_data)
            data.append(group_totals)
    
    totals['gp_percent'] = calculate_gp_percent(totals)
    data.append(totals)

    return columns, data

def get_all_data(filters, conditions, group_list):
    group_list_str = ','.join(f'"{group}"' for group in group_list)
    data = frappe.db.sql(f"""
        SELECT 
            si.name as voucher_no,
            dn.status,
            sii.item_code,
            sii.description,
            sii.qty,
            sii.base_net_amount,
            item.item_category,
            st.sales_person,
            IFNULL(
                (
                    SELECT 
                        sle.valuation_rate 
                    FROM 
                        `tabStock Ledger Entry` sle
                    WHERE 
                        sle.item_code = sii.item_code 
                        AND sle.voucher_type IN ('Delivery Note', 'Sales Invoice')
                        AND sle.warehouse = sii.warehouse
                        AND sle.voucher_no = IFNULL(
                            IF(si.is_return=0, 
                                IF(si.update_stock=0, sii.delivery_note, sii.parent), 
                                sii.delivery_note
                            ),
                            (
                                SELECT dni.parent 
                                FROM `tabDelivery Note Item` dni 
                                WHERE sii.sales_order=dni.against_sales_order 
                                LIMIT 1
                            )
                        )
                    LIMIT 1
                ) * IFNULL(sii.stock_qty, 0.0), 
                0.0
            ) AS item_cost,
            (sii.base_net_amount - IFNULL(
                (
                    SELECT 
                        sle.valuation_rate 
                    FROM 
                        `tabStock Ledger Entry` sle
                    WHERE 
                        sle.item_code = sii.item_code 
                        AND sle.voucher_type IN ('Delivery Note', 'Sales Invoice')
                        AND sle.warehouse = sii.warehouse
                        AND sle.voucher_no = IFNULL(
                            IF(si.is_return=0, 
                                IF(si.update_stock=0, sii.delivery_note, sii.parent), 
                                sii.delivery_note
                            ),
                            (
                                SELECT dni.parent 
                                FROM `tabDelivery Note Item` dni 
                                WHERE sii.sales_order=dni.against_sales_order 
                                LIMIT 1
                            )
                        )
                    LIMIT 1
                ) * IFNULL(sii.stock_qty, 0.0), 
                0.0
            )) AS gross_profit,
            si.{frappe.scrub(filters.groupby)} as {frappe.scrub(filters.groupby)}
        FROM 
            `tabSales Invoice View` si
            INNER JOIN `tabSales Invoice Item View` sii ON si.name = sii.parent
            LEFT JOIN `tabItem` item ON sii.item_code = item.name
            LEFT JOIN `tabSales Team` st ON st.parent = sii.parent
            LEFT JOIN `tabDelivery Note Item` dni ON sii.sales_order=dni.against_sales_order
            LEFT JOIN `tabDelivery Note` dn ON dni.parent = dn.name
        WHERE 
            si.docstatus = 1 AND si.{frappe.scrub(filters.groupby)} IN ({group_list_str}) {conditions}
    """, as_dict=True)
    return data

def calculate_totals(data):
    totals = {
        'qty': sum(d.get("qty", 0) for d in data),
        'base_net_amount': sum(d.get("base_net_amount", 0) for d in data),
        'item_cost': sum(d.get("item_cost", 0) for d in data),
        'gross_profit': sum(d.get("gross_profit", 0) for d in data),
        'gp_percent': 0.0
    }
    totals['gp_percent'] = calculate_gp_percent(totals)
    return totals

def update_totals(totals, group_totals):
    for key in ['qty', 'base_net_amount', 'item_cost', 'gross_profit']:
        totals[key] += group_totals[key]
    return totals

def calculate_gp_percent(totals):
    return round((totals.get("gross_profit", 0) / (totals.get("base_net_amount", 1))) * 100, 2)

def get_columns():
    columns = [
        {"fieldname": "item_code", "label": _("Item Code"), "fieldtype": "Data", "options": "Item", "width": 250},
        {"fieldname": "description", "label": _("Item Description"), "fieldtype": "Data", "width": 350},
        {"fieldname": "voucher_no", "label": _("Voucher No"), "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"fieldname": "qty", "label": _("Quantity"), "fieldtype": "Float", "width": 100},
        {"fieldname": "base_net_amount", "label": _("Amount"), "fieldtype": "Currency", "width": 150},
        {"fieldname": "item_cost", "label": _("Item Cost"), "fieldtype": "Currency", "width": 150},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 150},
        {"fieldname": "gross_profit", "label": _("Profit"), "fieldtype": "Currency", "width": 150},
        {"fieldname": "gp_percent", "label": _("Profit %"), "fieldtype": "Percentage", "width": 150},
        {"fieldname": "item_category", "label": _("Item Category"), "fieldtype": "Data", "width": 150},
        {"fieldname": "sales_person", "label": _("Sales Person"), "fieldtype": "Data", "width": 150},
    ]
    return columns

def get_conditions(filters):
    conditions = []
    if filters.brand:
        conditions.append(f"item.brand = '{filters.brand}'")
    if filters.company:
        conditions.append(f"si.company = '{filters.company}'")
    if filters.from_date:
        conditions.append(f"si.posting_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'")
    if filters.customer:
        customers = ','.join(f"'{customer}'" for customer in filters.customer)
        conditions.append(f"si.customer IN ({customers})")
    if filters.sales_person:
        sales_persons = ','.join(f"'{sp}'" for sp in filters.sales_person)
        conditions.append(f"st.sales_person IN ({sales_persons})")
    if filters.item_category:
        categories = ','.join(f"'{category}'" for category in filters.item_category)
        conditions.append(f"item.item_category IN ({categories})")
    if filters.cost_center:
        cost_centers = ','.join(f"'{cc}'" for cc in filters.cost_center)
        conditions.append(f"si.cost_center IN ({cost_centers})")
    if filters.department:
        departments = ','.join(f"'{department}'" for department in filters.department)
        conditions.append(f"si.department IN ({departments})")
    if filters.item_code:
        items = ','.join(f"'{item}'" for item in filters.item_code)
        conditions.append(f"sii.item_code IN ({items})")
    if filters.item_group:
        item_groups = ','.join(f"'{group}'" for group in filters.item_group)
        conditions.append(f"sii.item_group IN ({item_groups})")
    if filters.customer_group:
        customer_groups = ','.join(f"'{cg}'" for cg in filters.customer_group)
        conditions.append(f"si.customer_group IN ({customer_groups})")
    if filters.warehouse:
        warehouses = ','.join(f"'{wh}'" for wh in filters.warehouse)
        conditions.append(f"sii.warehouse IN ({warehouses})")
    if filters.territory:
        territories = ','.join(f"'{territory}'" for territory in filters.territory)
        conditions.append(f"si.territory IN ({territories})")

    return " AND " + " AND ".join(conditions) if conditions else ""
