# Copyright (c) 2023, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr

def execute(filters=None):
	columns, data = get_columns(), []
	conditions = get_conditions(filters)

	this_user = frappe.session.user
	this_user_has_roles = frappe.db.get_list('Has Role', {'parent': this_user}, pluck='role')
	workflow_list = frappe.db.get_list('Workflow', pluck='name')

	for wf in workflow_list:
		wf_doc = frappe.get_doc('Workflow', wf)
		dtype = wf_doc.get("document_type")
		approval_allowed_to = frappe.db.get_list('Workflow Transition', {'parent':dtype, 'action': ['in', ('Approve', 'Reject')]}, pluck='allowed')
		is_allowed = set([allowed for allowed in approval_allowed_to if allowed in this_user_has_roles])
		allowed_roles = ", ".join(is_allowed)

		if is_allowed:
			this_doc_data = frappe.db.sql("""SELECT '%s' as doctype, CONCAT("<a href='/app/", "%s", "/", name, "'", " target='_blank'>",name,"</a>") as name, workflow_state, owner
				FROM `tab%s`
				WHERE 1=1 AND workflow_state IN ('Draft', 'Quotation', 'Pending') %s"""%(dtype, dtype.lower().replace(" ","-"),dtype, conditions), as_dict=True)
			for d in this_doc_data:
				d['allowed_roles'] = allowed_roles

			data.extend(this_doc_data)
		
	return columns, data


def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and company='{}'".format(filters.get("company"))
	if filters.get("document_type"):
		conditions += " and doctype='{}'".format(filters.get("document_type"))
	if filters.get("owner"):
		conditions += " and owner='{}'".format(filters.get("owner"))
	if filters.get("from_date"):
		conditions += " and creation>='{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and creation<='{}'".format(filters.get("to_date"))

	return conditions


def get_columns():
	return [
		{
			'fieldname': 'doctype',
			'fieldtype': 'Data',
			'label': _('Document Type'),
			'width': 200,
		},
		{
			'fieldname': 'name',
			'fieldtype': 'Data',
			'label': _('Document Name'),
			'width': 200,
		},
		{
			'fieldname': 'workflow_state',
			'fieldtype': 'Data',
			'label': _('Workflow State'),
			'width': 150,
		},
		{
			'fieldname': 'allowed_roles',
			'fieldtype': 'Link',
			'options': 'Role',
			'label': _('Approver Role'),
			'width': 400
		},
		{
			'fieldname': 'owner',
			'fieldtype': 'Link',
			'options': 'User',
			'label': _('Created By'),
			'width': 300
		}
	]