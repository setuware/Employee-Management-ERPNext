import frappe

ADMIN_ROLES = ("System Manager", "HR Manager")


def is_admin():
	roles = frappe.get_roles()
	return bool(set(ADMIN_ROLES) & set(roles))


def require_admin():
	if not is_admin():
		frappe.throw("You do not have permission to perform this action")


def get_employee_for_user(user=None):
	if not user:
		user = frappe.session.user
	if user == "Administrator":
		return None
	return frappe.db.get_value("LMS Employee", {"user": user})
