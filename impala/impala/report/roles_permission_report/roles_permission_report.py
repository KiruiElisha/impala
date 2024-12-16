# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
import numpy as np
from frappe import _
from frappe.utils import get_site_name, cstr

def execute(filters=None):
	columns, data = get_columns(), get_role_permissions(filters)
	domain = get_site_name(frappe.local.request.host)
	role_list = frappe.db.get_list('Role', {'disabled' : 0}, pluck='name')
	myframe = {}
	if not filters:
		for role in role_list:
			role_in_data = any(role in d.values() for d in data)
			if not role_in_data:
				data.append({'role': role, 'name': '', 'permlevel': '', 'create': '', 'read': '', 'write': '', 'select': '', 'amend': '', 'print': '', 'report': '', 'email': '', 'import': '', 'export': '', 'share': '', 'submit': '', 'set_user_permissions': ''})


	# for role in role_list:
	# 	myframe.setdefault(role, {0: ['A', 'B'], 1 : ['C', 'D']})

	# for role in role_list:
	# 	for d in data:
	# 		myframe[role].append({'document' : d.get("name"), 'create': d.get("create"), 'write' : d.get("write"), 'read' : d.get("read"),'amend': d.get("amend"),\
	# 		'print': d.get("print"), 'report' : d.get("report"), 'export': d.get("export"), 'email': d.email, 'import': d.get("import"),\
	# 		'select': d.get("select"), 'share' : d.get("share"), 'submit' : d.get("submit"), 'set_user_permissions': d.get("set_user_permissions")})

	# df = pd.DataFrame.from_dict(myframe, orient='index')
	# with pd.ExcelWriter(domain + '-RolePermissions.xlsx') as writer:
	#     df.to_excel(writer, sheet_name='Role Permissions')


	df = pd.DataFrame.from_records(data)

	with pd.ExcelWriter(domain + '-RolePermissions.xlsx') as writer:
	    df.to_excel(writer, sheet_name='Role Permissions')

	return columns, data





def get_role_permissions(filters):
	conditions = ""
	if filters.role:
		conditions += " and dp.role = '{}'".format(filters.role)
	if filters.document:
		conditions += " and dt.name= '{}'".format(filters.document)
	data = frappe.db.sql("""
		SELECT 
			dp.role, dt.name, dp.permlevel, dp.create, dp.read, dp.write, dp.select, dp.amend, dp.print, dp.report, dp.email, dp.import, dp.export,
			dp.share, dp.submit, dp.set_user_permissions
			FROM `tabDocType` dt
			INNER JOIN `tabDocPerm` dp ON dt.name = dp.parent
			WHERE is_submittable=1 %s ORDER BY dp.role, dp.name
		"""%conditions, as_dict=True, debug=False)
	return data

def get_columns():
	return [
		{
			'fieldname': 'role',
			'fieldtype': 'Link',
			'options': 'Role',
			'label': _('Role'),
			'width': 200
		},
		{
			'fieldname': 'name',
			'fieldtype': 'Data',
			'label': _('Document'),
			'width': 180
		},
		{
			'fieldname': 'permlevel',
			'fieldtype': 'Data',
			'label': _('Perm Level'),
			'width': 80
		},
		{
			'fieldname': 'select',
			'fieldtype': 'Data',
			'label': _('Select'),
			'width': 80
		},
		{
			'fieldname': 'create',
			'fieldtype': 'Data',
			'label': _('Create'),
			'width': 80
		},
		{
			'fieldname': 'read',
			'fieldtype': 'Data',
			'label': _('Read'),
			'width': 80
		},
		{
			'fieldname': 'write',
			'fieldtype': 'Data',
			'label': _('Write'),
			'width': 80
		},
		{
			'fieldname': 'amend',
			'fieldtype': 'Data',
			'label': _('Ammend'),
			'width': 80
		},
		{
			'fieldname': 'print',
			'fieldtype': 'Data',
			'label': _('Print'),
			'width': 80
		},
		{
			'fieldname': 'report',
			'fieldtype': 'Data',
			'label': _('Report'),
			'width': 80
		},
		{
			'fieldname': 'email',
			'fieldtype': 'Data',
			'label': _('Email'),
			'width': 80
		},
		{
			'fieldname': 'import',
			'fieldtype': 'Data',
			'label': _('import'),
			'width': 80
		},
		{
			'fieldname': 'export',
			'fieldtype': 'Data',
			'label': _('Export'),
			'width': 80
		},
		{
			'fieldname': 'share',
			'fieldtype': 'Data',
			'label': _('Share'),
			'width': 80
		},
		{
			'fieldname': 'submit',
			'fieldtype': 'Data',
			'label': _('Submit'),
			'width': 80
		},
		{
			'fieldname': 'set_user_permissions',
			'fieldtype': 'Data',
			'label': _('Set User Permissions'),
			'width': 80
		},
	]