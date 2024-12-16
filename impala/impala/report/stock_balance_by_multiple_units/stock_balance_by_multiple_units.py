# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
from frappe.utils import flt

def execute(filters=None):
	if not filters:
		filters = {}
	conditions = get_conditions(filters)
	max_uoms = frappe.db.sql("""select c.uom from `tabBin` b  
		inner join `tabItem` item on b.item_code = item.name
		inner join `tabUOM Conversion Detail` c 
		on item.name = c.parent where 1=1 {} group by 1 order by 1""".format(conditions), as_dict=1)
	columns = get_column(max_uoms)
	data = []
	details = frappe.db.sql("""select b.item_code, item.item_name, item.item_group, 
		b.warehouse, item.stock_uom, b.actual_qty
		from `tabBin` b 
		inner join `tabItem` item on b.item_code = item.name
		where 1=1 {}
		""".format(conditions), as_dict=1)
	for d in details:
		row = {}
		row.update(d)
		for i in max_uoms:
			row[frappe.scrub(i.uom)] = 0
		row[frappe.scrub(d.stock_uom)] = d.actual_qty
		uoms = frappe.db.sql("""select conversion_factor, uom from `tabUOM Conversion Detail` 
			where parent = '{}' and uom != '{}'""".format(d.item_code, d.stock_uom), as_dict=1)
		for i in uoms:
			row[frappe.scrub(i.uom)] = flt(d.actual_qty or 0.0)/flt(i.conversion_factor or 1.0)

		data.append(row)

	return columns, data



def get_column(max_uoms):
	columns = [

		{
			"fieldname":"item_code",
			"label": "Item Code",
			"width": 100,
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname":"item_name",
			"label": "Item Name",
			"width": 150,
			"fieldtype": "Data",
		},
		{
			"fieldname":"item_group",
			"label": "Item Group",
			"width": 120,
			"fieldtype": "Link",
			"options": "Item Group"
		},
		{
			"fieldname":"warehouse",
			"label": "Warehouse",
			"width": 150,
			"options": "Warehouse",
			"fieldtype": "Link",
		},
	]

	for d in max_uoms:
		columns.append({
				"fieldname": frappe.scrub(d.uom),
				"label": d.uom,
				"width": 100,
				"fieldtype": "Float",
			})
	return columns



def get_conditions(filters):
	conditions = ""
	if filters.get("item_code"):
		conditions += " and b.item_code = '{}'".format(filters.get("item_code"))
	if filters.get("company"):
		conditions += " and item.company = '{}'".format(filters.get("company"))
	if filters.get("warehouse"):
		conditions += " and b.warehouse = '{}'".format(filters.get("warehouse"))

	return conditions