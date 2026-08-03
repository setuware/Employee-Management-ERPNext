import frappe

def validate_leave_request(doc, method):
	if doc.from_date and doc.to_date:
		if doc.to_date < doc.from_date:
			frappe.throw("To Date cannot be before From Date")
	
	if doc.employee:
		employee_exists = frappe.db.exists("Employee", doc.employee)
		if not employee_exists:
			frappe.throw(f"Employee {doc.employee} does not exist")
	
	if doc.status not in ["Pending", "Approved", "Rejected", "Canceled"]:
		frappe.throw("Invalid status. Must be Pending, Approved, Rejected, or Canceled")

def update_leave_status(doc, method):
	pass

def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	
	if "System Manager" in frappe.get_roles(user):
		return ""
	
	if "HR Manager" in frappe.get_roles(user):
		return ""
	
	return """(`tabLeave Request`.owner = '{user}')""".format(user=user)

def has_permission(doc, user=None, permission_type=None):
	if not user:
		user = frappe.session.user
	
	if "System Manager" in frappe.get_roles(user) or "HR Manager" in frappe.get_roles(user):
		return True
	
	if doc.owner == user:
		return True
	
	return False
