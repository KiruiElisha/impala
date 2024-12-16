# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = []
    data = []
    columns = get_cols(filters)
    data = get_data(filters)
    return columns, data


def get_data(filters):
    data = []
    data = data_according_to_their_relations_document_wise(
        filters.get("document_name"), filters.get("document_type"), filters
    )
    return data


def data_according_to_their_relations_document_wise(doc_name, doc_type, filters):
    data = []
    if doc_type == "Quotation":
        data = get_quotation_data(doc_name, filters)
    elif doc_type == "Sales Order":
        data = get_sales_order_data(doc_name, filters)
    elif doc_type == "Sales Invoice":
        data = get_sales_invoice_data(doc_name, filters)
    elif doc_type == "Delivery Note":
        data = get_delivery_notes_data(doc_name, filters)
    elif doc_type == "Material Request":
        data = get_material_request_data(doc_name, filters)
    elif doc_type == "Stock Entry":
        data = get_stock_entry_data(doc_name, filters)
    elif doc_type == "Purchase Order":
        data = get_purchase_order_data(doc_name, filters)
    elif doc_type == "Purchase Invoice":
        data = get_purchase_invoice_data(doc_name, filters)
    elif doc_type == "Purchase Receipt":
        data = get_purchase_receipt_data(doc_name, filters)
    return data


def get_data_query(doc_name, doctype):
    data_query = {
        "Quotation": f"""SELECT p.name, p.transaction_date as date, p.status, p.total_qty, p.base_grand_total FROM `tabQuotation` p inner join `tabQuotation Item` c on p.name = c.parent
			WHERE p.name = '{doc_name}' group by p.name """,
        "Sales Order": f"""SELECT p.name, p.transaction_date as date, p.status, p.total_qty, p.base_grand_total FROM `tabSales Order` p inner join `tabSales Order Item` c on p.name = c.parent
			WHERE p.name = '{doc_name}' group by p.name """,
        "Sales Invoice": f"""SELECT p.name, p.posting_date as date, p.status, p.total_qty, p.base_grand_total FROM `tabSales Invoice` p inner join `tabSales Invoice Item` c on p.name = c.parent
			WHERE p.name = '{doc_name}' group by p.name """,
        "Delivery Note": f"""SELECT p.name, p.posting_date as date, p.status, p.total_qty, p.base_grand_total FROM `tabDelivery Note` p inner join `tabDelivery Note Item` c on p.name = c.parent
			WHERE p.name = '{doc_name}' group by p.name """,
        "Material Request": f"""SELECT p.name, p.transaction_date as date, p.status, SUM(c.qty) as total_qty, "0" as base_grand_total FROM `tabMaterial Request` p inner join `tabMaterial Request Item` c on p.name = c.parent
			WHERE p.name = '{doc_name}' group by p.name """,
        "Stock Entry": f"""SELECT p.name, p.posting_date as date, p.docstatus as status , "0" as base_grand_total, SUM(c.qty) as total_qty  FROM `tabStock Entry` p inner join `tabStock Entry Detail` c on p.name = c.parent
			WHERE p.name = '{doc_name}' group by p.name """,
        "Purchase Order": f"""SELECT p.name, p.transaction_date as date, p.status, p.total_qty, p.base_grand_total FROM `tabPurchase Order` p inner join `tabPurchase Order Item` c on p.name = c.parent
			WHERE p.name = '{doc_name}' group by p.name """,
        "Purchase Invoice": f"""SELECT p.name, p.posting_date as date, p.status, p.total_qty, p.base_grand_total FROM `tabPurchase Invoice` p inner join `tabPurchase Invoice Item` c on p.name = c.parent
			WHERE p.name = '{doc_name}' group by p.name """,
        "Purchase Receipt": f"""SELECT p.name, p.posting_date as date, p.status, p.total_qty, p.base_grand_total FROM `tabPurchase Receipt` p inner join `tabPurchase Receipt Item` c on p.name = c.parent
			WHERE p.name = '{doc_name}' group by p.name """,
        "Payment Entry": f"""SELECT p.name, p.posting_date as date, p.status, "0" as total_qty, p.base_total_allocated_amount as base_grand_total FROM `tabPayment Entry` p inner join `tabPayment Entry Reference` c on p.name = c.parent
			WHERE p.name = '{doc_name}' group by p.name """,
    }
    return frappe.db.sql(
        data_query[doctype],
        as_dict=1,
        # debug=1,
    )


def get_relation_query(
    fields="p.name", condition="1=1", group_by="group by p.name", doctype="none"
):
    data_query = {
        "Quotation": f"""SELECT {fields} FROM `tabQuotation` p inner join `tabQuotation Item` c on p.name = c.parent WHERE {condition} {group_by} """,
        "Sales Order": f"""SELECT {fields} FROM `tabSales Order` p inner join `tabSales Order Item` c on p.name = c.parent WHERE {condition} {group_by} """,
        "Sales Invoice": f"""SELECT {fields} FROM `tabSales Invoice` p inner join `tabSales Invoice Item` c on p.name = c.parent WHERE {condition} {group_by} """,
        "Delivery Note": f"""SELECT {fields} FROM `tabDelivery Note` p inner join `tabDelivery Note Item` c on p.name = c.parent WHERE {condition} {group_by}""",
        "Material Request": f"""SELECT {fields} FROM `tabMaterial Request` p inner join `tabMaterial Request Item` c on p.name = c.parent WHERE {condition} {group_by} """,
        "Stock Entry": f"""SELECT {fields} FROM `tabStock Entry` p inner join `tabStock Entry Detail` c on p.name = c.parent WHERE {condition} {group_by} """,
        "Purchase Order": f"""SELECT {fields} FROM `tabPurchase Order` p inner join `tabPurchase Order Item` c on p.name = c.parent WHERE {condition} {group_by} """,
        "Purchase Invoice": f"""SELECT {fields} FROM `tabPurchase Invoice` p inner join `tabPurchase Invoice Item` c on p.name = c.parent WHERE {condition} {group_by} """,
        "Purchase Receipt": f"""SELECT {fields} FROM `tabPurchase Receipt` p inner join `tabPurchase Receipt Item` c on p.name = c.parent WHERE {condition} {group_by} """,
        "Payment Entry": f"""SELECT {fields} FROM `tabPayment Entry` p inner join `tabPayment Entry Reference` c on p.name = c.parent WHERE {condition} {group_by} """,
    }
    return frappe.db.sql(
        data_query[doctype],
        as_dict=1,
        # debug=1,
    )


def get_cols(filters):
    cols = [
        {
            "fieldname": "doctype",
            "label": "Reference Type",
            "fieldtype": "Link",
            "options": "DocType",
            "width": 200,
        },
        {
            "fieldname": "name",
            "label": "Reference name",
            "fieldtype": "Dynamic Link",
            "options": "doctype",
            "width": 200,
        },
        {
            "fieldname": "date",
            "label": "Date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "fieldname": "total_qty",
            "label": "Total Qty",
            "fieldtype": "float",
            "width": 100,
        },
        {
            "fieldname": "base_grand_total",
            "label": "Grand Total",
            "fieldtype": "Currency",
            "width": 200,
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Data",
            "width": 200,
        },
    ]
    return cols


def get_quotation_data(name, filters):
    data = []
    Sales_Order_Data = get_relation_query(
        fields="p.name as name, c.prevdoc_docname as relation",
        condition=f"c.prevdoc_docname = '{name}'",
        doctype="Sales Order",
    )
    for sod in Sales_Order_Data:
        sod_data = get_data_query(sod.get("name"), "Sales Order")
        for d in sod_data:
            d["doctype"] = "Sales Order"
            data.append(d)
    Quotation_Sales_Order_List = convert_list_for_sql(
        [d["name"] for d in Sales_Order_Data]
    )

    Sales_Invoice_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation",
        condition=f"c.sales_order in {Quotation_Sales_Order_List}",
        doctype="Sales Invoice",
    )
    Quotation_Sales_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Sales_Invoice_Data]
    )
    for sid in Sales_Invoice_Data:
        sid_data = get_data_query(sid.get("name"), "Sales Invoice")
        for d in sid_data:
            d["doctype"] = "Sales Invoice"
            data.append(d)

    Delivery_Note_Data = get_relation_query(
        fields="p.name as name, c.against_sales_order as relation",
        condition=f"c.against_sales_order in {Quotation_Sales_Order_List}",
        doctype="Delivery Note",
    )
    for dnd in Delivery_Note_Data:
        dnd_data = get_data_query(dnd.get("name"), "Delivery Note")
        for d in dnd_data:
            d["doctype"] = "Delivery Note"
            data.append(d)
    Material_Request_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.sales_order in {Quotation_Sales_Order_List}",
        doctype="Material Request",
    )
    Material_Request_sales_order_List = convert_list_for_sql(
        [d["name"] for d in Material_Request_Data]
    )
    for mrd in Material_Request_Data:
        mrd_data = get_data_query(mrd.get("name"), "Material Request")
        for d in mrd_data:
            d["doctype"] = "Material Request"
            data.append(d)

    Stock_Entry_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request  in {Material_Request_sales_order_List}",
        doctype="Stock Entry",
    )
    for sed in Stock_Entry_Data:
        sed_data = get_data_query(sed.get("name"), "Stock Entry")
        for d in sed_data:
            d["doctype"] = "Stock Entry"
            if d["status"] == 0:
                d["status"] = "Draft"
            elif d["status"] == 1:
                d["status"] = "Submitted"
            elif d["status"] == 2:
                d["status"] = "Cancelled"
            data.append(d)

    Purchase_Order_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request in {Material_Request_sales_order_List}",
        doctype="Purchase Order",
    )
    for pod in Purchase_Order_Data:
        pod_data = get_data_query(pod.get("name"), "Purchase Order")
        for d in pod_data:
            d["doctype"] = "Purchase Order"
            data.append(d)

    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Order_Data]
    )

    Purchase_Invoice_Data = get_relation_query(
        fields="p.name as name, c.purchase_receipt as relation",
        condition=f"c.purchase_order in {Material_Request_Purchase_Order_List}",
        doctype="Purchase Invoice",
    )
    Purchase_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Invoice_Data]
    )
    for pid in Purchase_Invoice_Data:
        pid_data = get_data_query(pid.get("name"), "Purchase Invoice")
        for d in pid_data:
            d["doctype"] = "Purchase Invoice"
            data.append(d)

    Material_Request_Purchase_Receipt_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Invoice_Data]
    )
    Purchase_Receipt_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"p.name in {Material_Request_Purchase_Receipt_List}",
        doctype="Purchase Receipt",
    )
    for prd in Purchase_Receipt_Data:
        prd_data = get_data_query(prd.get("name"), "Purchase Receipt")
        for d in prd_data:
            d["doctype"] = "Purchase Receipt"
            data.append(d)

    Payment_Entry_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.reference_name in {(*Quotation_Sales_Order_List, *Quotation_Sales_Invoice_List, *Purchase_Invoice_List)}",
        doctype="Payment Entry",
    )
    for ped in Payment_Entry_Data:
        ped_data = get_data_query(ped.get("name"), "Payment Entry")
        for d in ped_data:
            d["doctype"] = "Payment Entry"
            data.append(d)

    return data


def get_sales_order_data(name, filters):
    data = []
    Sales_Order_Data = get_relation_query(
        fields="c.prevdoc_docname as relation",
        condition=f"p.name = '{name}'",
        doctype="Sales Order",
    )
    Sales_Order_Quotation_List = convert_list_for_sql(
        [d["relation"] for d in Sales_Order_Data if d["relation"]]
    )
    Quotation_Data = get_relation_query(
        fields="p.name as name",
        condition=f"p.name in {Sales_Order_Quotation_List}",
        doctype="Quotation",
    )
    for qd in Quotation_Data:
        qd_data = get_data_query(qd.get("name"), "Quotation")
        for d in qd_data:
            d["doctype"] = "Quotation"
            data.append(d)

    Sales_Invoice_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation",
        condition=f"c.sales_order = '{name}'",
        doctype="Sales Invoice",
    )
    Sales_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Sales_Invoice_Data if d["name"]]
    )
    for sid in Sales_Invoice_Data:
        sid_data = get_data_query(sid.get("name"), "Sales Invoice")
        for d in sid_data:
            d["doctype"] = "Sales Invoice"
            data.append(d)

    Delivery_Note_Data = get_relation_query(
        fields="p.name as name, c.against_sales_order as relation",
        condition=f"c.against_sales_order = '{name}'",
        doctype="Delivery Note",
    )
    for dnd in Delivery_Note_Data:
        dnd_data = get_data_query(dnd.get("name"), "Delivery Note")
        for d in dnd_data:
            d["doctype"] = "Delivery Note"
            data.append(d)
    Material_Request_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.sales_order = '{name}' ",
        doctype="Material Request",
    )
    Material_Request_sales_order_List = convert_list_for_sql(
        [d["name"] for d in Material_Request_Data]
    )
    for mrd in Material_Request_Data:
        mrd_data = get_data_query(mrd.get("name"), "Material Request")
        for d in mrd_data:
            d["doctype"] = "Material Request"
            data.append(d)

    Stock_Entry_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request  in {Material_Request_sales_order_List}",
        doctype="Stock Entry",
    )
    for sed in Stock_Entry_Data:
        sed_data = get_data_query(sed.get("name"), "Stock Entry")
        for d in sed_data:
            d["doctype"] = "Stock Entry"
            if d["status"] == 0:
                d["status"] = "Draft"
            elif d["status"] == 1:
                d["status"] = "Submitted"
            elif d["status"] == 2:
                d["status"] = "Cancelled"
            data.append(d)

    Purchase_Order_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request in {Material_Request_sales_order_List}",
        doctype="Purchase Order",
    )
    for pod in Purchase_Order_Data:
        pod_data = get_data_query(pod.get("name"), "Purchase Order")
        for d in pod_data:
            d["doctype"] = "Purchase Order"
            data.append(d)

    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Order_Data]
    )

    Purchase_Invoice_Data = get_relation_query(
        fields="p.name as name, c.purchase_receipt as relation",
        condition=f"c.purchase_order in {Material_Request_Purchase_Order_List}",
        doctype="Purchase Invoice",
    )
    Purchase_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Invoice_Data]
    )
    for pid in Purchase_Invoice_Data:
        pid_data = get_data_query(pid.get("name"), "Purchase Invoice")
        for d in pid_data:
            d["doctype"] = "Purchase Invoice"
            data.append(d)

    Material_Request_Purchase_Receipt_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Invoice_Data]
    )
    Purchase_Receipt_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"p.name in {Material_Request_Purchase_Receipt_List}",
        doctype="Purchase Receipt",
    )
    for prd in Purchase_Receipt_Data:
        prd_data = get_data_query(prd.get("name"), "Purchase Receipt")
        for d in prd_data:
            d["doctype"] = "Purchase Receipt"
            data.append(d)

    Payment_Entry_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.reference_name in {(name, *Sales_Invoice_List, *Purchase_Invoice_List)}",
        doctype="Payment Entry",
    )
    for ped in Payment_Entry_Data:
        ped_data = get_data_query(ped.get("name"), "Payment Entry")
        for d in ped_data:
            d["doctype"] = "Payment Entry"
            data.append(d)

    return data


def get_sales_invoice_data(name, filters):
    data = []
    Sales_Invoice_Data = get_relation_query(
        fields="c.sales_order as relation",
        condition=f"p.name = '{name}'",
        doctype="Sales Invoice",
    )
    Sales_Invoice_Sales_Order_List = convert_list_for_sql(
        [d["relation"] for d in Sales_Invoice_Data if d["relation"]]
    )

    Sales_Order_Data = get_relation_query(
        fields="p.name as name, c.prevdoc_docname as relation",
        condition=f"p.name in {Sales_Invoice_Sales_Order_List}",
        doctype="Sales Order",
    )
    for sod in Sales_Order_Data:
        sod_data = get_data_query(sod.get("name"), "Sales Order")
        for d in sod_data:
            d["doctype"] = "Sales Order"
            data.append(d)
    Sales_Order_Quotation_List = convert_list_for_sql(
        [d["relation"] for d in Sales_Order_Data if d["relation"]]
    )

    Quotation_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"p.name in {Sales_Order_Quotation_List}",
        doctype="Quotation",
    )
    for qd in Quotation_Data:
        qd_data = get_data_query(qd.get("name"), "Quotation")
        for d in qd_data:
            d["doctype"] = "Quotation"
            data.append(d)

    Delivery_Note_Data = get_relation_query(
        fields="p.name as name, c.against_sales_order as relation",
        condition=f"c.against_sales_order in {Sales_Invoice_Sales_Order_List}",
        doctype="Delivery Note",
    )
    for dnd in Delivery_Note_Data:
        dnd_data = get_data_query(dnd.get("name"), "Delivery Note")
        for d in dnd_data:
            d["doctype"] = "Delivery Note"
            data.append(d)

    Material_Request_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.sales_order in {Sales_Invoice_Sales_Order_List} ",
        doctype="Material Request",
    )
    Material_Request_sales_order_List = convert_list_for_sql(
        [d["name"] for d in Material_Request_Data]
    )
    for mrd in Material_Request_Data:
        mrd_data = get_data_query(mrd.get("name"), "Material Request")
        for d in mrd_data:
            d["doctype"] = "Material Request"
            data.append(d)

    Stock_Entry_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request  in {Material_Request_sales_order_List}",
        doctype="Stock Entry",
    )
    for sed in Stock_Entry_Data:
        sed_data = get_data_query(sed.get("name"), "Stock Entry")
        for d in sed_data:
            d["doctype"] = "Stock Entry"
            if d["status"] == 0:
                d["status"] = "Draft"
            elif d["status"] == 1:
                d["status"] = "Submitted"
            elif d["status"] == 2:
                d["status"] = "Cancelled"
            data.append(d)

    Purchase_Order_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request in {Material_Request_sales_order_List}",
        doctype="Purchase Order",
    )
    for pod in Purchase_Order_Data:
        pod_data = get_data_query(pod.get("name"), "Purchase Order")
        for d in pod_data:
            d["doctype"] = "Purchase Order"
            data.append(d)

    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Order_Data]
    )

    Purchase_Invoice_Data = get_relation_query(
        fields="p.name as name, c.purchase_receipt as relation",
        condition=f"c.purchase_order in {Material_Request_Purchase_Order_List}",
        doctype="Purchase Invoice",
    )
    Purchase_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Invoice_Data]
    )
    for pid in Purchase_Invoice_Data:
        pid_data = get_data_query(pid.get("name"), "Purchase Invoice")
        for d in pid_data:
            d["doctype"] = "Purchase Invoice"
            data.append(d)

    Material_Request_Purchase_Receipt_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Invoice_Data]
    )
    Purchase_Receipt_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"p.name in {Material_Request_Purchase_Receipt_List}",
        doctype="Purchase Receipt",
    )
    for prd in Purchase_Receipt_Data:
        prd_data = get_data_query(prd.get("name"), "Purchase Receipt")
        for d in prd_data:
            d["doctype"] = "Purchase Receipt"
            data.append(d)

    Payment_Entry_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.reference_name in {(name, *Sales_Invoice_Sales_Order_List, *Purchase_Invoice_List)}",
        doctype="Payment Entry",
    )
    for ped in Payment_Entry_Data:
        ped_data = get_data_query(ped.get("name"), "Payment Entry")
        for d in ped_data:
            d["doctype"] = "Payment Entry"
            data.append(d)
    return data


def get_delivery_notes_data(name, filters):
    data = []
    Delivery_Note_Data = get_relation_query(
        fields="p.name as name, c.against_sales_order as relation ",
        condition=f"p.name = '{name}'",
        doctype="Delivery Note",
        group_by="group by c.against_sales_order"
    )
    Delivery_Note_Sales_Order_List = convert_list_for_sql(
        [d["relation"] for d in Delivery_Note_Data]
    )
    Sales_Order_Data = get_relation_query(
        fields="p.name as name, c.prevdoc_docname as relation",
        condition=f"p.name in {Delivery_Note_Sales_Order_List}",
        doctype="Sales Order",
    )
    for sod in Sales_Order_Data:
        sod_data = get_data_query(sod.get("name"), "Sales Order")
        for d in sod_data:
            d["doctype"] = "Sales Order"
            data.append(d)
    Sales_Order_Quotation_List = convert_list_for_sql(
        [d["relation"] for d in Sales_Order_Data if d["relation"]]
    )
    Sales_Order_List = convert_list_for_sql(
        [d["name"] for d in Sales_Order_Data if d["name"]]
    )
    Sales_Invoice_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation",
        condition=f"c.sales_order in {Sales_Order_List}",
        doctype="Sales Invoice",
    )
    Sales_Inv_List = convert_list_for_sql(
        [d["name"] for d in Sales_Invoice_Data if d["name"]]
    )
    for sid in Sales_Invoice_Data:
        sid_data = get_data_query(sid.get("name"), "Sales Invoice")
        for d in sid_data:
            d["doctype"] = "Sales Invoice"
            data.append(d)
    Quotation_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"p.name in {Sales_Order_Quotation_List}",
        doctype="Quotation",
    )
    for qd in Quotation_Data:
        qd_data = get_data_query(qd.get("name"), "Quotation")
        for d in qd_data:
            d["doctype"] = "Quotation"
            data.append(d)

    Material_Request_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.sales_order in {Sales_Order_List} ",
        doctype="Material Request",
    )
    Material_Request_sales_order_List = convert_list_for_sql(
        [d["name"] for d in Material_Request_Data]
    )
    for mrd in Material_Request_Data:
        mrd_data = get_data_query(mrd.get("name"), "Material Request")
        for d in mrd_data:
            d["doctype"] = "Material Request"
            data.append(d)

    Stock_Entry_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request  in {Material_Request_sales_order_List}",
        doctype="Stock Entry",
    )
    for sed in Stock_Entry_Data:
        sed_data = get_data_query(sed.get("name"), "Stock Entry")
        for d in sed_data:
            d["doctype"] = "Stock Entry"
            if d["status"] == 0:
                d["status"] = "Draft"
            elif d["status"] == 1:
                d["status"] = "Submitted"
            elif d["status"] == 2:
                d["status"] = "Cancelled"
            data.append(d)

    Purchase_Order_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request in {Material_Request_sales_order_List}",
        doctype="Purchase Order",
    )
    for pod in Purchase_Order_Data:
        pod_data = get_data_query(pod.get("name"), "Purchase Order")
        for d in pod_data:
            d["doctype"] = "Purchase Order"
            data.append(d)

    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Order_Data]
    )

    Purchase_Invoice_Data = get_relation_query(
        fields="p.name as name, c.purchase_receipt as relation",
        condition=f"c.purchase_order in {Material_Request_Purchase_Order_List}",
        doctype="Purchase Invoice",
    )
    Purchase_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Invoice_Data]
    )
    for pid in Purchase_Invoice_Data:
        pid_data = get_data_query(pid.get("name"), "Purchase Invoice")
        for d in pid_data:
            d["doctype"] = "Purchase Invoice"
            data.append(d)

    Material_Request_Purchase_Receipt_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Invoice_Data]
    )
    Purchase_Receipt_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"p.name in {Material_Request_Purchase_Receipt_List}",
        doctype="Purchase Receipt",
    )
    for prd in Purchase_Receipt_Data:
        prd_data = get_data_query(prd.get("name"), "Purchase Receipt")
        for d in prd_data:
            d["doctype"] = "Purchase Receipt"
            data.append(d)

    Payment_Entry_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.reference_name in {(*Sales_Inv_List, *Sales_Order_List, *Purchase_Invoice_List)}",
        doctype="Payment Entry",
    )
    for ped in Payment_Entry_Data:
        ped_data = get_data_query(ped.get("name"), "Payment Entry")
        for d in ped_data:
            d["doctype"] = "Payment Entry"
            data.append(d)
    return data


def get_material_request_data(name, filters):
    data = []
    Stock_Entry_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request = '{name}'",
        doctype="Stock Entry",
    )
    for sed in Stock_Entry_Data:
        sed_data = get_data_query(sed.get("name"), "Stock Entry")
        for d in sed_data:
            d["doctype"] = "Stock Entry"
            if d["status"] == 0:
                d["status"] = "Draft"
            elif d["status"] == 1:
                d["status"] = "Submitted"
            elif d["status"] == 2:
                d["status"] = "Cancelled"
            data.append(d)

    Purchase_Order_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request = '{name}'",
        doctype="Purchase Order",
    )
    for pod in Purchase_Order_Data:
        pod_data = get_data_query(pod.get("name"), "Purchase Order")
        for d in pod_data:
            d["doctype"] = "Purchase Order"
            data.append(d)

    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Order_Data]
    )

    Purchase_Invoice_Data = get_relation_query(
        fields="p.name as name, c.purchase_receipt as relation",
        condition=f"c.purchase_order in {Material_Request_Purchase_Order_List}",
        doctype="Purchase Invoice",
    )
    Purchase_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Invoice_Data]
    )
    for pid in Purchase_Invoice_Data:
        pid_data = get_data_query(pid.get("name"), "Purchase Invoice")
        for d in pid_data:
            d["doctype"] = "Purchase Invoice"
            data.append(d)

    Material_Request_Purchase_Receipt_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Invoice_Data]
    )
    Purchase_Receipt_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"p.name in {Material_Request_Purchase_Receipt_List}",
        doctype="Purchase Receipt",
    )
    for prd in Purchase_Receipt_Data:
        prd_data = get_data_query(prd.get("name"), "Purchase Receipt")
        for d in prd_data:
            d["doctype"] = "Purchase Receipt"
            data.append(d)

    Material_Request_Data = get_relation_query(
        fields="c.sales_order as relation",
        condition=f"p.name = '{name}'",
        doctype="Material Request",
        group_by="",
    )
    Material_Request_sales_order_List = convert_list_for_sql(
        [d["relation"] for d in Material_Request_Data]
    )
    Sales_Order_Data = get_relation_query(
        fields="p.name as name, c.prevdoc_docname as relation",
        condition=f"p.name in {Material_Request_sales_order_List}",
        doctype="Sales Order",
    )
    for sod in Sales_Order_Data:
        sod_data = get_data_query(sod.get("name"), "Sales Order")
        for d in sod_data:
            d["doctype"] = "Sales Order"
            data.append(d)
    Sales_Order_Quotation_List = convert_list_for_sql(
        [d["relation"] for d in Sales_Order_Data if d["relation"]]
    )
    Quotation_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"p.name in {Sales_Order_Quotation_List}",
        doctype="Quotation",
    )
    for qd in Quotation_Data:
        qd_data = get_data_query(qd.get("name"), "Quotation")
        for d in qd_data:
            d["doctype"] = "Quotation"
            data.append(d)

    Sales_Invoice_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation",
        condition=f"c.sales_order in {Material_Request_sales_order_List}",
        doctype="Sales Invoice",
    )
    Sales_Inv_List = convert_list_for_sql(
        [d["name"] for d in Sales_Invoice_Data if d["name"]]
    )
    for sid in Sales_Invoice_Data:
        sid_data = get_data_query(sid.get("name"), "Sales Invoice")
        for d in sid_data:
            d["doctype"] = "Sales Invoice"
            data.append(d)

    Delivery_Note_Data = get_relation_query(
        fields="p.name as name, c.against_sales_order as relation",
        condition=f"c.against_sales_order in {Material_Request_sales_order_List}",
        doctype="Delivery Note",
    )
    for dnd in Delivery_Note_Data:
        dnd_data = get_data_query(dnd.get("name"), "Delivery Note")
        for d in dnd_data:
            d["doctype"] = "Delivery Note"
            data.append(d)

    Payment_Entry_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.reference_name in {(*Purchase_Invoice_List,*Sales_Inv_List, *Material_Request_sales_order_List)}",
        doctype="Payment Entry",
    )
    for ped in Payment_Entry_Data:
        ped_data = get_data_query(ped.get("name"), "Payment Entry")
        for d in ped_data:
            d["doctype"] = "Payment Entry"
            data.append(d)
    return data


def get_purchase_order_data(name, filters):
    data = []
    Purchase_Order_Data = get_relation_query(
        fields="p.name as name, c.material_request as relation",
        condition=f"p.name = '{name}'",
        doctype="Purchase Order",
    )

    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Order_Data if d["relation"]]
    )

    Material_Request_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation ",
        condition=f"p.name in {Material_Request_Purchase_Order_List}",
        doctype="Material Request",
    )
    for mrd in Material_Request_Data:
        mrd_data = get_data_query(mrd.get("name"), "Material Request")
        for d in mrd_data:
            d["doctype"] = "Material Request"
            data.append(d)
    Material_Request_sales_order_List = convert_list_for_sql(
        [d["relation"] for d in Material_Request_Data]
    )
    Stock_Entry_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request in {Material_Request_Purchase_Order_List}",
        doctype="Stock Entry",
    )
    for sed in Stock_Entry_Data:
        sed_data = get_data_query(sed.get("name"), "Stock Entry")
        for d in sed_data:
            d["doctype"] = "Stock Entry"
            if d["status"] == 0:
                d["status"] = "Draft"
            elif d["status"] == 1:
                d["status"] = "Submitted"
            elif d["status"] == 2:
                d["status"] = "Cancelled"
            data.append(d)

    Purchase_Invoice_Data = get_relation_query(
        fields="p.name as name, c.purchase_receipt as relation",
        condition=f"c.purchase_order = '{name}'",
        doctype="Purchase Invoice",
    )
    for pid in Purchase_Invoice_Data:
        pid_data = get_data_query(pid.get("name"), "Purchase Invoice")
        for d in pid_data:
            d["doctype"] = "Purchase Invoice"
            data.append(d)

    Purchase_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Invoice_Data if d["name"]]
    )
    Material_Request_Purchase_Receipt_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Invoice_Data if d["relation"]]
    )
    Purchase_Receipt_Data = get_relation_query(
        fields="p.name as name",
        condition=f"p.name in {Material_Request_Purchase_Receipt_List}",
        doctype="Purchase Receipt",
    )
    for prd in Purchase_Receipt_Data:
        prd_data = get_data_query(prd.get("name"), "Purchase Receipt")
        for d in prd_data:
            d["doctype"] = "Purchase Receipt"
            data.append(d)

    Sales_Order_Data = get_relation_query(
        fields="p.name as name, c.prevdoc_docname as relation",
        condition=f"p.name in {Material_Request_sales_order_List} ",
        doctype="Sales Order",
    )
    Sales_Order_Quotation_List = convert_list_for_sql(
        [d["relation"] for d in Sales_Order_Data if d["relation"]]
    )
    for sod in Sales_Order_Data:
        sod_data = get_data_query(sod.get("name"), "Sales Order")
        for d in sod_data:
            d["doctype"] = "Sales Order"
            data.append(d)

    Sales_Invoice_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation",
        condition=f"c.sales_order in {Material_Request_sales_order_List}",
        doctype="Sales Invoice",
    )
    Sales_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Sales_Invoice_Data if d["name"]]
    )
    for sid in Sales_Invoice_Data:
        sid_data = get_data_query(sid.get("name"), "Sales Invoice")
        for d in sid_data:
            d["doctype"] = "Sales Invoice"
            data.append(d)
    Quotation_Data = get_relation_query(
        fields="p.name as name",
        condition=f"p.name in {Sales_Order_Quotation_List}",
        doctype="Quotation",
    )
    for qd in Quotation_Data:
        qd_data = get_data_query(qd.get("name"), "Quotation")
        for d in qd_data:
            d["doctype"] = "Quotation"
            data.append(d)

    Delivery_Note_Data = get_relation_query(
        fields="p.name as name, c.against_sales_order as relation",
        condition=f"c.against_sales_order in {Material_Request_sales_order_List}",
        doctype="Delivery Note",
    )
    for dnd in Delivery_Note_Data:
        dnd_data = get_data_query(dnd.get("name"), "Delivery Note")
        for d in dnd_data:
            d["doctype"] = "Delivery Note"
            data.append(d)

    Payment_Entry_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.reference_name in {(*Purchase_Invoice_List, *Material_Request_sales_order_List, *Sales_Invoice_List)}",
        doctype="Payment Entry",
    )
    for ped in Payment_Entry_Data:
        ped_data = get_data_query(ped.get("name"), "Payment Entry")
        for d in ped_data:
            d["doctype"] = "Payment Entry"
            data.append(d)

    return data


def get_stock_entry_data(name, filters):
    data = []
    Stock_Entry_Data = get_relation_query(
        fields="c.material_request as relation",
        condition=f"p.name = '{name}'",
        doctype="Stock Entry",
    )
    Stock_Entry_Material_Request_List = convert_list_for_sql(
        [d["relation"] for d in Stock_Entry_Data if d["relation"]]
    )
    Material_Request_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation ",
        condition=f"p.name in {Stock_Entry_Material_Request_List}",
        doctype="Material Request",
    )
    for mrd in Material_Request_Data:
        mrd_data = get_data_query(mrd.get("name"), "Material Request")
        for d in mrd_data:
            d["doctype"] = "Material Request"
            data.append(d)

    Purchase_Order_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.material_request in {Stock_Entry_Material_Request_List}",
        doctype="Purchase Order",
    )
    for pod in Purchase_Order_Data:
        pod_data = get_data_query(pod.get("name"), "Purchase Order")
        for d in pod_data:
            d["doctype"] = "Purchase Order"
            data.append(d)

    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Order_Data]
    )

    Purchase_Invoice_Data = get_relation_query(
        fields="p.name as name, c.purchase_receipt as relation",
        condition=f"c.purchase_order in {Material_Request_Purchase_Order_List}",
        doctype="Purchase Invoice",
    )
    for pid in Purchase_Invoice_Data:
        pid_data = get_data_query(pid.get("name"), "Purchase Invoice")
        for d in pid_data:
            d["doctype"] = "Purchase Invoice"
            data.append(d)

    Purchase_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Invoice_Data if d["name"]]
    )
    Material_Request_Purchase_Receipt_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Invoice_Data if d["relation"]]
    )
    Purchase_Receipt_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"p.name in {Material_Request_Purchase_Receipt_List}",
        doctype="Purchase Receipt",
    )
    for prd in Purchase_Receipt_Data:
        prd_data = get_data_query(prd.get("name"), "Purchase Receipt")
        for d in prd_data:
            d["doctype"] = "Purchase Receipt"
            data.append(d)

    Material_Request_sales_order_List = convert_list_for_sql(
        [d["relation"] for d in Material_Request_Data]
    )
    Sales_Order_Data = get_relation_query(
        fields="p.name as name, c.prevdoc_docname as relation",
        condition=f"p.name in {Material_Request_sales_order_List} ",
        doctype="Sales Order",
    )
    Sales_Order_Quotation_List = convert_list_for_sql(
        [d["relation"] for d in Sales_Order_Data if d["relation"]]
    )
    for sod in Sales_Order_Data:
        sod_data = get_data_query(sod.get("name"), "Sales Order")
        for d in sod_data:
            d["doctype"] = "Sales Order"
            data.append(d)

    Sales_Invoice_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation",
        condition=f"c.sales_order in {Material_Request_sales_order_List}",
        doctype="Sales Invoice",
    )
    Sales_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Sales_Invoice_Data if d["name"]]
    )
    for sid in Sales_Invoice_Data:
        sid_data = get_data_query(sid.get("name"), "Sales Invoice")
        for d in sid_data:
            d["doctype"] = "Sales Invoice"
            data.append(d)
    Quotation_Data = get_relation_query(
        fields="p.name as name",
        condition=f"p.name in {Sales_Order_Quotation_List}",
        doctype="Quotation",
    )
    for qd in Quotation_Data:
        qd_data = get_data_query(qd.get("name"), "Quotation")
        for d in qd_data:
            d["doctype"] = "Quotation"
            data.append(d)

    Delivery_Note_Data = get_relation_query(
        fields="p.name as name, c.against_sales_order as relation",
        condition=f"c.against_sales_order in {Material_Request_sales_order_List}",
        doctype="Delivery Note",
    )
    for dnd in Delivery_Note_Data:
        dnd_data = get_data_query(dnd.get("name"), "Delivery Note")
        for d in dnd_data:
            d["doctype"] = "Delivery Note"
            data.append(d)

    Payment_Entry_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.reference_name in {(*Purchase_Invoice_List, *Sales_Invoice_List, *Material_Request_sales_order_List)}",
        doctype="Payment Entry",
    )
    for ped in Payment_Entry_Data:
        ped_data = get_data_query(ped.get("name"), "Payment Entry")
        for d in ped_data:
            d["doctype"] = "Payment Entry"
            data.append(d)

    return data


def get_purchase_invoice_data(name, filters):
    data = []
    Purchase_Invoice_Data = get_relation_query(
        fields="p.name as name, c.purchase_order as relation,c.purchase_receipt as another_relation",
        condition=f"p.name = '{name}'",
        doctype="Purchase Invoice",
        group_by="",
    )

    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Invoice_Data if d["relation"]]
    )
    Purchase_Order_Data = get_relation_query(
        fields="p.name as name, c.material_request as relation",
        condition=f"p.name in {Material_Request_Purchase_Order_List}",
        doctype="Purchase Order",
    )
    for pod in Purchase_Order_Data:
        pod_data = get_data_query(pod.get("name"), "Purchase Order")
        for d in pod_data:
            d["doctype"] = "Purchase Order"
            data.append(d)
    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Order_Data if d["relation"]]
    )
    Material_Request_Data = get_relation_query(
        fields="p.name as name , c.sales_order as relation ",
        condition=f"p.name in {Material_Request_Purchase_Order_List}",
        doctype="Material Request",
    )
    for mrd in Material_Request_Data:
        mrd_data = get_data_query(mrd.get("name"), "Material Request")
        for d in mrd_data:
            d["doctype"] = "Material Request"
            data.append(d)

    Stock_Entry_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request in {Material_Request_Purchase_Order_List} ",
        doctype="Stock Entry",
    )
    for sed in Stock_Entry_Data:
        sed_data = get_data_query(sed.get("name"), "Stock Entry")
        for d in sed_data:
            d["doctype"] = "Stock Entry"
            if d["status"] == 0:
                d["status"] = "Draft"
            elif d["status"] == 1:
                d["status"] = "Submitted"
            elif d["status"] == 2:
                d["status"] = "Cancelled"
            data.append(d)

    Material_Request_Purchase_Receipt_List = convert_list_for_sql(
        [d["another_relation"] for d in Purchase_Invoice_Data if d["another_relation"]]
    )
    Purchase_Receipt_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"p.name in {Material_Request_Purchase_Receipt_List}",
        doctype="Purchase Receipt",
    )
    for prd in Purchase_Receipt_Data:
        prd_data = get_data_query(prd.get("name"), "Purchase Receipt")
        for d in prd_data:
            d["doctype"] = "Purchase Receipt"
            data.append(d)
    Material_Request_sales_order_List = convert_list_for_sql(
        [d["relation"] for d in Material_Request_Data]
    )
    Sales_Order_Data = get_relation_query(
        fields="p.name as name, c.prevdoc_docname as relation",
        condition=f"p.name in {Material_Request_sales_order_List} ",
        doctype="Sales Order",
    )
    Sales_Order_Quotation_List = convert_list_for_sql(
        [d["relation"] for d in Sales_Order_Data if d["relation"]]
    )
    for sod in Sales_Order_Data:
        sod_data = get_data_query(sod.get("name"), "Sales Order")
        for d in sod_data:
            d["doctype"] = "Sales Order"
            data.append(d)

    Sales_Invoice_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation",
        condition=f"c.sales_order in {Material_Request_sales_order_List}",
        doctype="Sales Invoice",
    )
    Sales_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Sales_Invoice_Data if d["name"]]
    )
    for sid in Sales_Invoice_Data:
        sid_data = get_data_query(sid.get("name"), "Sales Invoice")
        for d in sid_data:
            d["doctype"] = "Sales Invoice"
            data.append(d)
    Quotation_Data = get_relation_query(
        fields="p.name as name",
        condition=f"p.name in {Sales_Order_Quotation_List}",
        doctype="Quotation",
    )
    for qd in Quotation_Data:
        qd_data = get_data_query(qd.get("name"), "Quotation")
        for d in qd_data:
            d["doctype"] = "Quotation"
            data.append(d)

    Delivery_Note_Data = get_relation_query(
        fields="p.name as name, c.against_sales_order as relation",
        condition=f"c.against_sales_order in {Material_Request_sales_order_List}",
        doctype="Delivery Note",
    )
    for dnd in Delivery_Note_Data:
        dnd_data = get_data_query(dnd.get("name"), "Delivery Note")
        for d in dnd_data:
            d["doctype"] = "Delivery Note"
            data.append(d)

    Payment_Entry_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.reference_name in {(name, *Material_Request_sales_order_List, *Sales_Invoice_List)}",
        doctype="Payment Entry",
    )
    for ped in Payment_Entry_Data:
        ped_data = get_data_query(ped.get("name"), "Payment Entry")
        for d in ped_data:
            d["doctype"] = "Payment Entry"
            data.append(d)
    return data


def get_purchase_receipt_data(name, filters):
    data = []
    Purchase_Invoice_Data = get_relation_query(
        fields="p.name as name, c.purchase_order as relation ",
        condition=f"c.purchase_receipt = '{name}'",
        doctype="Purchase Invoice",
    )
    for pid in Purchase_Invoice_Data:
        pid_data = get_data_query(pid.get("name"), "Purchase Invoice")
        for d in pid_data:
            d["doctype"] = "Purchase Invoice"
            data.append(d)

    Purchase_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Purchase_Invoice_Data if d["name"]]
    )
    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Invoice_Data if d["relation"]]
    )

    Purchase_Order_Data = get_relation_query(
        fields="p.name as name, c.material_request as relation ",
        condition=f"p.name in {Material_Request_Purchase_Order_List}",
        doctype="Purchase Order",
    )
    for pod in Purchase_Order_Data:
        pod_data = get_data_query(pod.get("name"), "Purchase Order")
        for d in pod_data:
            d["doctype"] = "Purchase Order"
            data.append(d)
    Material_Request_Purchase_Order_List = convert_list_for_sql(
        [d["relation"] for d in Purchase_Order_Data if d["relation"]]
    )

    Material_Request_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation ",
        condition=f"p.name in {Material_Request_Purchase_Order_List}",
        doctype="Material Request",
    )
    for mrd in Material_Request_Data:
        mrd_data = get_data_query(mrd.get("name"), "Material Request")
        for d in mrd_data:
            d["doctype"] = "Material Request"
            data.append(d)

    Stock_Entry_Data = get_relation_query(
        fields="p.name as name ",
        condition=f"c.material_request in {Material_Request_Purchase_Order_List}",
        doctype="Stock Entry",
    )
    for sed in Stock_Entry_Data:
        sed_data = get_data_query(sed.get("name"), "Stock Entry")
        for d in sed_data:
            d["doctype"] = "Stock Entry"
            if d["status"] == 0:
                d["status"] = "Draft"
            elif d["status"] == 1:
                d["status"] = "Submitted"
            elif d["status"] == 2:
                d["status"] = "Cancelled"
            data.append(d)
    Material_Request_sales_order_List = convert_list_for_sql(
        [d["relation"] for d in Material_Request_Data]
    )
    Sales_Order_Data = get_relation_query(
        fields="p.name as name, c.prevdoc_docname as relation",
        condition=f"p.name in {Material_Request_sales_order_List} ",
        doctype="Sales Order",
    )
    Sales_Order_Quotation_List = convert_list_for_sql(
        [d["relation"] for d in Sales_Order_Data if d["relation"]]
    )
    for sod in Sales_Order_Data:
        sod_data = get_data_query(sod.get("name"), "Sales Order")
        for d in sod_data:
            d["doctype"] = "Sales Order"
            data.append(d)

    Sales_Invoice_Data = get_relation_query(
        fields="p.name as name, c.sales_order as relation",
        condition=f"c.sales_order in {Material_Request_sales_order_List}",
        doctype="Sales Invoice",
    )
    Sales_Invoice_List = convert_list_for_sql(
        [d["name"] for d in Sales_Invoice_Data if d["name"]]
    )
    for sid in Sales_Invoice_Data:
        sid_data = get_data_query(sid.get("name"), "Sales Invoice")
        for d in sid_data:
            d["doctype"] = "Sales Invoice"
            data.append(d)
    Quotation_Data = get_relation_query(
        fields="p.name as name",
        condition=f"p.name in {Sales_Order_Quotation_List}",
        doctype="Quotation",
    )
    for qd in Quotation_Data:
        qd_data = get_data_query(qd.get("name"), "Quotation")
        for d in qd_data:
            d["doctype"] = "Quotation"
            data.append(d)

    Delivery_Note_Data = get_relation_query(
        fields="p.name as name, c.against_sales_order as relation",
        condition=f"c.against_sales_order in {Material_Request_sales_order_List}",
        doctype="Delivery Note",
    )
    for dnd in Delivery_Note_Data:
        dnd_data = get_data_query(dnd.get("name"), "Delivery Note")
        for d in dnd_data:
            d["doctype"] = "Delivery Note"
            data.append(d)

    Payment_Entry_Data = get_relation_query(
        fields="p.name as name",
        condition=f"c.reference_name in {(*Purchase_Invoice_List, *Material_Request_sales_order_List, *Sales_Invoice_List)}",
        doctype="Payment Entry",
    )
    for ped in Payment_Entry_Data:
        ped_data = get_data_query(ped.get("name"), "Payment Entry")
        for d in ped_data:
            d["doctype"] = "Payment Entry"
            data.append(d)

    return data


def convert_list_for_sql(any_list=[]):
    any_list.append("abcdefghijklmnopqrstuvwxyz1234567890")
    any_list.append("abcdefghijklmnopqrstuvwxyz1234567890")
    any_list = [a for a in any_list if a]
    any_list = tuple(any_list)
    return any_list
