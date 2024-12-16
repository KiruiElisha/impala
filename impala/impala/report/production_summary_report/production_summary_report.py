# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):

	conditions = get_conditions(filters)

	sql_query = """ 
		SELECT `tabStock Entry Detail`.item_code, `tabStock Entry Detail`.item_name, SUM(`tabStock Entry Detail`.transfer_qty) as qty
		FROM `tabStock Entry`
		INNER JOIN `tabStock Entry Detail` ON `tabStock Entry`.name=`tabStock Entry Detail`.parent
		WHERE `tabStock Entry`.docstatus=1 and `tabStock Entry`.stock_entry_type='Manufacture' %s
		GROUP BY `tabStock Entry Detail`.item_code ORDER BY `tabStock Entry Detail`.item_code
		
	""" %conditions

	
	data = frappe.db.sql(sql_query, as_dict=True, debug=True)
	columns = get_columns()
	return columns, data


def get_conditions(filters):
	conditions = ""

	if filters.company:
		conditions += " and `tabStock Entry`.company = '%s'"%filters.company
	if filters.date_range:
		conditions += " and `tabStock Entry`.posting_date BETWEEN '%s' AND '%s'"%(filters.date_range[0], filters.date_range[1])
	if filters.item_type:
		if filters.item_type=="Finished":
			conditions += " and	`tabStock Entry Detail`.is_finished_item=1"
		if filters.item_type=="Scrap":
			conditions += " and	`tabStock Entry Detail`.is_scrap_item=1"
	else:
		conditions += " and	(`tabStock Entry Detail`.is_finished_item=1 OR `tabStock Entry Detail`.is_scrap_item=1)"

	return conditions


def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"align": "left",
			"width": 460
		},
		{
			"fieldname": "qty",
			"label": _("Qty"),
			"fieldtype": "Float",
			"width": 160,
		}
	]