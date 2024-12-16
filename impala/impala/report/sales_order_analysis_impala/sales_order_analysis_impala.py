# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import copy

import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate


def execute(filters=None):
	if not filters:
		return [], [], None, []

	validate_filters(filters)

	columns = get_columns(filters)
	conditions = get_conditions(filters)
	data = get_data(conditions, filters)

	if not data:
		return [], [], None, []

	data, chart_data = prepare_data(data, filters)

	return columns, data, None, chart_data

def validate_filters(filters):
	from_date, to_date = filters.get("from_date"), filters.get("to_date")

	if not from_date and to_date:
		frappe.throw(_("From and To Dates are required."))
	elif date_diff(to_date, from_date) < 0:
		frappe.throw(_("To Date cannot be before From Date."))

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and so.transaction_date between %(from_date)s and %(to_date)s"

	if filters.get("company"):
		conditions += " and so.company = %(company)s"

	if filters.get("sales_order"):
		conditions += " and so.name in %(sales_order)s"

	if filters.get("status"):
		conditions += " and so.status in %(status)s"

	if filters.get("project"):
		conditions += " and so.project = '{}'".format(filters.get("project"))

	if filters.get("cost_center"):
		conditions += " and so.cost_center = '{}'".format(filters.get("cost_center"))
	if filters.get("department"):
		conditions += " and so.department = '{}'".format(filters.get("department"))
	if filters.get("item_group"):
		conditions += " and (select item_group from `tabItem` where name=soi.item_code) = '{}'".format(filters.get("item_group"))
	if filters.get("customer_group"):
		conditions += " and (select customer_group from `tabCustomer` where name=so.customer) = '{}'".format(filters.get("customer_group"))

	return conditions

def get_data(conditions, filters):
	data = frappe.db.sql("""
		SELECT
			so.transaction_date as date,
			soi.delivery_date as delivery_date,
			so.name as sales_order,
			so.status, so.customer, soi.item_code,
			DATEDIFF(CURDATE(), soi.delivery_date) as delay_days,
			IF(so.status in ('Completed','To Bill'), 0, (SELECT delay_days)) as delay,
			soi.qty, soi.delivered_qty,
			(soi.qty - soi.delivered_qty) AS pending_qty,
			IFNULL(SUM(sii.qty), 0) as billed_qty,
			soi.base_amount as amount,
			(soi.delivered_qty * soi.base_rate) as delivered_qty_amount,
			(soi.billed_amt * IFNULL(so.conversion_rate, 1)) as billed_amount,
			(soi.base_amount - (soi.billed_amt * IFNULL(so.conversion_rate, 1))) as pending_amount,
			soi.warehouse as warehouse,
			so.company, soi.name,
			soi.description as description,
			so.department as department,
			so.cost_center as cost_center,
			so.project as project,
			(select customer_group from `tabCustomer` where name=so.customer) as customer_group,
			(select item_group from `tabItem` where name=soi.item_code) as item_group
		FROM
			`tabSales Order` so,
			`tabSales Order Item` soi
		LEFT JOIN `tabSales Invoice Item` sii
			ON sii.so_detail = soi.name and sii.docstatus = 1
		WHERE
			soi.parent = so.name
			and so.status not in ('Stopped', 'Closed', 'On Hold')
			and so.docstatus = 1
			{conditions}
		GROUP BY soi.name
		ORDER BY so.transaction_date ASC
	""".format(conditions=conditions), filters, as_dict=1)

	return data

def prepare_data(data, filters):
	completed, pending = 0, 0

	if filters.get("group_by_so"):
		sales_order_map = {}

	for row in data:
		# sum data for chart
		completed += row["billed_amount"]
		pending += row["pending_amount"]

		# prepare data for report view
		row["qty_to_bill"] = flt(row["qty"]) - flt(row["billed_qty"])

		row["delay"] = 0 if row["delay"] and row["delay"] < 0 else row["delay"]
		if filters.get("group_by_so"):
			so_name = row["sales_order"]

			if not so_name in sales_order_map:
				# create an entry
				row_copy = copy.deepcopy(row)
				sales_order_map[so_name] = row_copy
			else:
				# update existing entry
				so_row = sales_order_map[so_name]
				so_row["required_date"] = max(getdate(so_row["delivery_date"]), getdate(row["delivery_date"]))
				so_row["delay"] = min(so_row["delay"], row["delay"])

				# sum numeric columns
				fields = ["qty", "delivered_qty", "pending_qty", "billed_qty", "qty_to_bill", "amount",
					"delivered_qty_amount", "billed_amount", "pending_amount"]
				for field in fields:
					so_row[field] = flt(row[field]) + flt(so_row[field])

	chart_data = prepare_chart_data(pending, completed)

	if filters.get("group_by_so"):
		data = []
		for so in sales_order_map:
			data.append(sales_order_map[so])
		return data, chart_data

	return data, chart_data

def prepare_chart_data(pending, completed):
	labels = ["Amount to Bill", "Billed Amount"]

	return {
		"data" : {
			"labels": labels,
			"datasets": [
				{"values": [pending, completed]}
				]
		},
		"type": 'donut',
		"height": 300
	}

def get_columns(filters):
	columns = [
		{
			"label":_("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 90
		},
		{
			"label": _("Sales Order"),
			"fieldname": "sales_order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 160
		},
		{
			"label":_("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 130
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 130
		},
		{

			"fieldname": "customer_group",
			"label": _("Customer Group"),
			"fieldtype": "Link",
			"options" : "Customer Group",
			"width": 100
		}
		]

	if not filters.get("group_by_so"):
		columns.extend([
		{
			"label":_("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 100
		},
		{

		"fieldname": "item_group",
		"label": _("Item Group"),
		"fieldtype": "Link",
		"options" : "Item Group",
		"width": 150
		}
		])
		columns.append({
			"label":_("Description"),
			"fieldname": "description",
			"fieldtype": "Small Text",
			"width": 100
		})

	columns.extend([
		{
			"label": _("Qty"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 120,
			"convertible": "qty"
		},
		{
			"label": _("Delivered Qty"),
			"fieldname": "delivered_qty",
			"fieldtype": "Float",
			"width": 120,
			"convertible": "qty"
		},
		{
			"label": _("Qty to Deliver"),
			"fieldname": "pending_qty",
			"fieldtype": "Float",
			"width": 120,
			"convertible": "qty"
		},
		{
			"label": _("Billed Qty"),
			"fieldname": "billed_qty",
			"fieldtype": "Float",
			"width": 80,
			"convertible": "qty"
		},
		{
			"label": _("Qty to Bill"),
			"fieldname": "qty_to_bill",
			"fieldtype": "Float",
			"width": 80,
			"convertible": "qty"
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 110,
			"options": "Company:company:default_currency",
			"convertible": "rate"
		},
		{
			"label": _("Billed Amount"),
			"fieldname": "billed_amount",
			"fieldtype": "Currency",
			"width": 110,
			"options": "Company:company:default_currency",
			"convertible": "rate"
		},
		{
			"label": _("Pending Amount"),
			"fieldname": "pending_amount",
			"fieldtype": "Currency",
			"width": 130,
			"options": "Company:company:default_currency",
			"convertible": "rate"
		},
		{
			"label": _("Amount Delivered"),
			"fieldname": "delivered_qty_amount",
			"fieldtype": "Currency",
			"width": 100,
			"options": "Company:company:default_currency",
			"convertible": "rate"
		},
		{
			"label":_("Delivery Date"),
			"fieldname": "delivery_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Delay (in Days)"),
			"fieldname": "delay",
			"fieldtype": "Data",
			"width": 100
		}
	])
	if not filters.get("group_by_so"):
		columns.append({
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 100
		})
	columns.extend([
		{

			"fieldname": "cost_center",
			"label": _("Division"),
			"options" : "Cost Center",
			"fieldtype": "Link",
			"width": 100
		},
		{

			"fieldname": "department",
			"label": _("Department"),
			"fieldtype": "Link",
			"options" : "Department",
			"width": 150
		},
		{

			"fieldname": "project",
			"label": _("Project"),
			"fieldtype": "Link",
			"options" : "Project",
			"width": 100
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 100
		}
		])


	return columns
