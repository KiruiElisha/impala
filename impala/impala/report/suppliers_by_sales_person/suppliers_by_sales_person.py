# Copyright (c) 2024, Codes Soft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, fmt_money
from collections import defaultdict

def execute(filters=None):
	if not filters:
		filters = {}
	
	validate_filters(filters)
	set_user_permissions(filters)
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data

def set_user_permissions(filters):
	"""Check if current user is sales person"""
	if not frappe.session.user == "Administrator":
		filters["owner"] = frappe.session.user

def validate_filters(filters):
	if not filters.get("company"):
		frappe.throw(_("Company is required"))
	if not filters.get("from_date"):
		filters["from_date"] = frappe.defaults.get_user_default("year_start_date")
	if not filters.get("to_date"):
		filters["to_date"] = frappe.defaults.get_user_default("year_end_date")

def get_columns():
	return [
		{
			"fieldname": "sales_person",
			"label": _("Sales Person"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "total_suppliers",
			"label": _("Total Suppliers"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "total_invoices",
			"label": _("Total Invoices"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "paid_amount",
			"label": _("Paid Amount"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "outstanding_amount",
			"label": _("Outstanding Amount"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "payment_ratio",
			"label": _("Payment Ratio %"),
			"fieldtype": "Percent",
			"width": 120
		},
		{
			"fieldname": "avg_payment_days",
			"label": _("Avg. Payment Days"),
			"fieldtype": "Float",
			"width": 150,
			"precision": 1
		},
		{
			"fieldname": "total_suppliers_overdue",
			"label": _("Suppliers Overdue"),
			"fieldtype": "Int",
			"width": 150
		}
	]

def get_data(filters):
	data = []
	sales_person_data = defaultdict(lambda: {
		"sales_person": "",
		"total_suppliers": 0,
		"total_invoices": 0,
		"paid_amount": 0,
		"outstanding_amount": 0,
		"payment_ratio": 0,
		"avg_payment_days": 0,
		"total_suppliers_overdue": 0,
		"payment_days_total": 0,
		"payment_days_count": 0,
		"suppliers": set()
	})
	
	# Build supplier filters
	supplier_filters = {
		"disabled": 0,
		"company": filters.get("company")
	}
	
	if filters.get("supplier_group"):
		supplier_filters["supplier_group"] = filters.get("supplier_group")
	if filters.get("owner"):
		supplier_filters["owner"] = filters.get("owner")
	
	# Get suppliers using get_list
	suppliers = frappe.get_list("Supplier",
		filters=supplier_filters,
		fields=["name", "supplier_name", "supplier_group", "owner", "modified_by"],
		order_by="name"
	)
	
	for supplier in suppliers:
		# Get creator's full name
		sales_person = frappe.db.get_value("User", supplier.owner, "full_name") or supplier.owner
		
		# Get invoice data
		invoices = frappe.get_list("Purchase Invoice",
			filters={
				"supplier": supplier.name,
				"docstatus": 1,
				"posting_date": ["between", [filters.get("from_date"), filters.get("to_date")]],
				"company": filters.get("company")
			},
			fields=["name", "grand_total", "paid_amount", "outstanding_amount", 
				   "posting_date", "due_date"]
		)
		
		if not invoices:
			continue
		
		# Get payment entries
		payments = frappe.get_list("Payment Entry",
			filters={
				"party_type": "Supplier",
				"party": supplier.name,
				"docstatus": 1,
				"posting_date": ["between", [filters.get("from_date"), filters.get("to_date")]],
				"company": filters.get("company")
			},
			fields=["paid_amount", "posting_date"]
		)
		
		# Calculate metrics
		total_invoices = sum(inv.grand_total for inv in invoices)
		invoice_payments = sum(inv.paid_amount for inv in invoices)
		additional_payments = sum(pe.paid_amount for pe in payments)
		total_paid = invoice_payments + additional_payments
		outstanding = total_invoices - total_paid
		
		# Calculate payment days
		for inv in invoices:
			if inv.paid_amount > 0:
				payment = next((p for p in payments if p.posting_date >= inv.posting_date), None)
				if payment:
					days = (payment.posting_date - inv.posting_date).days
					sales_person_data[sales_person]["payment_days_total"] += days
					sales_person_data[sales_person]["payment_days_count"] += 1
		
		# Update sales person data
		sales_person_data[sales_person]["sales_person"] = sales_person
		sales_person_data[sales_person]["suppliers"].add(supplier.name)
		sales_person_data[sales_person]["total_invoices"] += total_invoices
		sales_person_data[sales_person]["paid_amount"] += total_paid
		sales_person_data[sales_person]["outstanding_amount"] += outstanding
		
		# Count overdue suppliers
		if any(inv.outstanding_amount > 0 and inv.due_date < nowdate() for inv in invoices):
			sales_person_data[sales_person]["total_suppliers_overdue"] += 1
	
	# Prepare final data
	for sp_data in sales_person_data.values():
		sp_data["total_suppliers"] = len(sp_data["suppliers"])
		if sp_data["total_invoices"]:
			sp_data["payment_ratio"] = (sp_data["paid_amount"] / sp_data["total_invoices"]) * 100
		if sp_data["payment_days_count"]:
			sp_data["avg_payment_days"] = sp_data["payment_days_total"] / sp_data["payment_days_count"]
		
		# Remove temporary fields
		del sp_data["payment_days_total"]
		del sp_data["payment_days_count"]
		del sp_data["suppliers"]
		
		data.append(sp_data)
	
	# Sort by total invoices
	data.sort(key=lambda x: x["total_invoices"], reverse=True)
	
	return data
