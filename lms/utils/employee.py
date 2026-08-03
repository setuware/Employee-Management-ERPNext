import frappe

def validate_employee(doc, method):
	if doc.email:
		if "@" not in doc.email or doc.email.count("@") != 1:
			frappe.throw("Invalid email format")
	
	if doc.employee_id:
		existing = frappe.db.exists("Employee", {
			"employee_id": doc.employee_id,
			"name": ["!=", doc.name]
		})
		if existing:
			frappe.throw(f"Employee ID {doc.employee_id} already exists")

def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	
	if "System Manager" in frappe.get_roles(user):
		return ""
	
	return """(`tabEmployee`.owner = '{user}')""".format(user=user)

def has_permission(doc, user=None, permission_type=None):
	if not user:
		user = frappe.session.user
	
	if "System Manager" in frappe.get_roles(user) or "HR Manager" in frappe.get_roles(user):
		return True
	
	if doc.owner == user:
		return True
	
	return False
