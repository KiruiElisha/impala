# Copyright (c) 2024, Codes Soft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(), get_date(filters)
	return columns, data


def get_columns():
	return [
		{"label": "Production Plan", "fieldname": "production_plan", "fieldtype": "Link", "options": "Production Plan", "width": 150},
		{"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": "Required Qty", "fieldname": "required_qty", "fieldtype": "Float", "width": 150},
		{"label": "Production Qty", "fieldname": "production_qty", "fieldtype": "Float", "width": 150},
	]


def get_date(filters=None):
	strquery = """
			select distinct po.name as production_plan, woi.item_code, sum(woi.required_qty) as required_qty, poi.conversion_factor * poi.new_qty as production_qty
			from `tabWork Order` as wo
			inner join `tabWork Order Item` as woi on wo.name = woi.parent
			inner join `tabProduction Plan` as po on po.name = wo.production_plan
			left join `tabMaterial Request Plan Item` as poi on poi.parent = po.name and poi.item_code = woi.item_code
			where po.docstatus = 1 and wo.docstatus = 1 
			"""
		
	if filters.get("production_plan"):
		strquery = strquery + " and po.name = '"+ filters.get("production_plan") + "'"

	if filters.get("from_date"):
		strquery = strquery + " and po.posting_date >= '" + filters.get("from_date") + "'"

	if filters.get("to_date"):
		strquery = strquery + " and po.posting_date <= '"+ filters.get("to_date") + "'"

	strquery = strquery + " group by po.name, woi.item_code order by po.name"

	res = frappe.db.sql(strquery, as_list = 1)

	results = []
	pp = ''
	for r in res:
		if pp != r[0]:
			results.append([r[0], '', '', ''])
			pp = r[0]
		
		results.append(['', r[1], r[2], r[3]])

	return results
