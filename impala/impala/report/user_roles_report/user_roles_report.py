# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.file_manager import save_file, save_file_on_filesystem
from frappe.utils import cstr
import pandas as pd
import numpy as np
from frappe.utils.xlsxutils import make_xlsx, build_xlsx_response


def execute(filters=None):
	if not filters:
		filters = frappe._dict()
	columns, data = get_columns(), get_data(filters)

	myframe = {}
	for d in data:
		cols = frappe._dict()
		myframe.setdefault(d.get("full_name"), [])
	
	for d in data:
		myframe[d.get("full_name")].append(d.get("role"))

	df = pd.DataFrame.from_dict(myframe, orient='index')
	df = df.transpose()
	cols_width = []
	for d in myframe:
		cols_width.append(150)

	with pd.ExcelWriter('UserHasRoles.xlsx') as writer:
	    df.to_excel(writer, sheet_name='User Roles')

	return columns, data


def get_data(filters):
	conditions = ""
	if filters.user:
		users = filters.user
		if len(users)<2:
			users.append("")
		users = tuple(users)
		conditions += " and u.name IN {}".format(users)
	data = frappe.db.sql("""
		SELECT 
			u.full_name, hr.role
			FROM `tabUser` u
			INNER JOIN `tabHas Role` hr ON u.name = hr.parent
			WHERE u.enabled=1 {} 
		""".format(conditions), as_dict=True)

	return data


def get_columns():
	return [
		{
			'fieldname': 'full_name',
			'fieldtype': 'Data',
			'label': _('Username'),
			'width': 400,
		},
		{
			'fieldname': 'role',
			'fieldtype': 'Link',
			'options': 'Role',
			'label': _('Role'),
			'width': 360,
		},
	]


# save_file('UserHasRoles.xlsx', myframe, 'Report', 'User Roles Report')
# make_xlsx(myframe, 'User Roles', column_widths=cols_width)	
# content = build_xlsx_response(myframe, 'UserHasRoles.xlsx')
# save_file_on_filesystem('UserHasRoles.xlsx', content, content_type='xlsx', is_private=0)