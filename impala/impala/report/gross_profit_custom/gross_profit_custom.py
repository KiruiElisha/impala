# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _, scrub
from frappe.utils import flt, cint
from erpnext.stock.utils import get_incoming_rate
from collections import defaultdict

def execute(filters=None):
    if not filters:
        filters = frappe._dict()
    
    filters.currency = frappe.get_cached_value('Company', filters.company, "default_currency")
    
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {
            "label": _("Sales Invoice"),
            "fieldname": "sales_invoice",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 150
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link", 
            "options": "Customer",
            "width": 150
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Delivery Note"),
            "fieldname": "delivery_note",
            "fieldtype": "Link",
            "options": "Delivery Note",
            "width": 200
        },
        {
            "label": _("Selling Amount"),
            "fieldname": "selling_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "label": _("Buying Amount"),
            "fieldname": "buying_amount", 
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "label": _("Gross Profit"),
            "fieldname": "gross_profit",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "label": _("Gross Profit %"),
            "fieldname": "gross_profit_percent",
            "fieldtype": "Percent",
            "width": 150
        },
        {
            "fieldname": "currency",
            "label": _("Currency"),
            "fieldtype": "Link",
            "options": "Currency",
            "hidden": 1
        }
    ]

def get_data(filters):
    invoices = get_invoices(filters)
    if not invoices:
        return []
        
    stock_ledger_entries = get_stock_ledger_entries(filters, invoices)
    non_stock_items = get_non_stock_items()
    
    data = []
    for inv in invoices:
        invoice_buying_amount = 0.0
        
        # Get items for this invoice
        items = get_invoice_items(inv.name)
        delivery_notes = get_delivery_notes(inv.name)
        
        for item in items:
            buying_amount = 0.0
            
            if item.is_stock_item:
                buying_amount = get_buying_amount_from_sle(item, stock_ledger_entries)
            else:
                buying_amount = get_last_purchase_rate(item) * item.stock_qty
                
            if item.is_return:
                buying_amount *= -1
                
            invoice_buying_amount += buying_amount
            
        # Calculate invoice profit
        selling_amount = flt(inv.base_net_total)
        buying_amount = flt(invoice_buying_amount)
        gross_profit = flt(selling_amount - buying_amount)
        
        # Calculate percentage with proper precision
        gross_profit_percent = 0.0
        if selling_amount:
            gross_profit_percent = flt((gross_profit / selling_amount) * 100.0, 2)
        
        data.append({
            "sales_invoice": inv.name,
            "customer": inv.customer,
            "customer_name": inv.customer_name,
            "delivery_note": ', '.join(delivery_notes) if delivery_notes else '',
            "selling_amount": selling_amount,
            "buying_amount": buying_amount,
            "gross_profit": gross_profit,
            "gross_profit_percent": gross_profit_percent,
            "currency": filters.currency
        })
            
    return data

def get_invoices(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
    
    where_clause = " AND " + " AND ".join(conditions) if conditions else ""
    
    return frappe.db.sql("""
        SELECT 
            name,
            customer,
            customer_name,
            base_net_total,
            currency,
            conversion_rate
        FROM 
            `tabSales Invoice`
        WHERE 
            docstatus = 1 
            AND company = %(company)s
            AND is_opening != 'Yes'
            AND is_return != 1
            {where_clause}
        ORDER BY 
            posting_date DESC, name DESC
    """.format(where_clause=where_clause), filters, as_dict=1)

def get_invoice_items(invoice):
    return frappe.db.sql("""
        SELECT 
            sii.item_code,
            sii.item_name,
            sii.stock_qty,
            sii.qty,
            sii.uom,
            sii.conversion_factor,
            sii.base_net_amount,
            sii.base_net_rate,
            sii.warehouse,
            sii.incoming_rate,
            sii.base_rate,
            sii.item_tax_template,
            i.valuation_method,
            i.is_stock_item,
            si.update_stock,
            si.is_return,
            COALESCE(sii.delivery_note, '') as delivery_note,
            COALESCE(sii.dn_detail, '') as dn_detail
        FROM 
            `tabSales Invoice Item` sii
        LEFT JOIN
            `tabItem` i ON sii.item_code = i.name
        LEFT JOIN
            `tabSales Invoice` si ON sii.parent = si.name
        WHERE 
            sii.parent = %s
            AND sii.docstatus = 1
        ORDER BY
            sii.idx
    """, invoice, as_dict=1)

def get_stock_ledger_entries(filters, invoices):
    """Get stock ledger entries with value difference"""
    invoice_items = frappe.db.sql("""
        SELECT DISTINCT item_code 
        FROM `tabSales Invoice Item`
        WHERE parent in %s
    """, [tuple([d.name for d in invoices])], as_dict=1)
    
    if not invoice_items:
        return []
        
    return frappe.db.sql("""
        SELECT 
            item_code,
            warehouse,
            posting_date,
            actual_qty as qty,
            stock_value,
            valuation_rate
        FROM 
            `tabStock Ledger Entry`
        WHERE 
            company = %(company)s
            AND is_cancelled = 0
            AND item_code in %(items)s
            AND posting_date <= %(to_date)s
        ORDER BY
            posting_date DESC, posting_time DESC, creation DESC
    """, {
        "company": filters.company,
        "items": [d.item_code for d in invoice_items],
        "to_date": filters.to_date
    }, as_dict=1)

def get_buying_amount_from_sle(item, stock_ledger_entries):
    """Get buying amount based on stock ledger entries"""
    buying_amount = 0.0
    
    # First priority: Use incoming_rate from invoice item
    if item.incoming_rate:
        return flt(item.incoming_rate * item.stock_qty)
    
    # Second priority: Get from stock ledger entries
    sle_list = [sle for sle in stock_ledger_entries 
               if sle.item_code == item.item_code 
               and sle.warehouse == item.warehouse]
               
    if sle_list:
        # Get the latest SLE before this transaction
        for sle in sle_list:
            if sle.voucher_type == item.parenttype and sle.voucher_no == item.parent:
                if sle.valuation_rate:
                    buying_amount = flt(sle.valuation_rate * item.stock_qty)
                    break
    
    # Third priority: Get from Bin
    if not buying_amount:
        valuation_rate = frappe.db.get_value("Bin", 
            {"item_code": item.item_code, "warehouse": item.warehouse},
            "valuation_rate")
        if valuation_rate:
            buying_amount = flt(valuation_rate * item.stock_qty)
    
    return buying_amount

def get_buying_amount_from_item_rate(item, company):
    """Get buying amount based on valuation method"""
    valuation_rate = frappe.db.get_value("Bin", 
        {"item_code": item.item_code, "warehouse": item.warehouse},
        "valuation_rate")
        
    if not valuation_rate:
        valuation_rate = frappe.db.get_value("Item", item.item_code, "valuation_rate")
        
    return flt(valuation_rate) * flt(item.stock_qty)

def get_last_purchase_rate(item):
    """Get last purchase rate for non-stock items"""
    last_purchase = frappe.db.sql("""
        SELECT 
            base_rate,
            conversion_factor,
            uom
        FROM `tabPurchase Invoice Item`
        WHERE 
            item_code = %s
            AND docstatus = 1
        ORDER BY creation DESC
        LIMIT 1
    """, item.item_code, as_dict=1)
    
    if last_purchase:
        conversion_factor = flt(last_purchase[0].conversion_factor) or 1.0
        if last_purchase[0].uom != item.uom:
            # Get conversion factor if UOMs are different
            target_conversion = frappe.db.get_value("UOM Conversion Detail",
                {"parent": item.item_code, "uom": item.uom},
                "conversion_factor") or 1.0
            conversion_factor = conversion_factor / target_conversion
            
        return flt(last_purchase[0].base_rate) * conversion_factor
    return 0

def get_delivery_notes(invoice):
    return frappe.db.sql_list("""
        SELECT DISTINCT delivery_note
        FROM `tabSales Invoice Item`
        WHERE parent = %s
            AND delivery_note IS NOT NULL
            AND docstatus = 1
    """, invoice)

def get_non_stock_items():
    return set(frappe.db.sql_list("""
        SELECT name
        FROM `tabItem`
        WHERE is_stock_item = 0
    """))
