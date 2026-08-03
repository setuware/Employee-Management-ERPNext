import frappe


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/attendance-log"
		raise frappe.Redirect

	if not ("System Manager" in frappe.get_roles() or "HR Manager" in frappe.get_roles()):
		frappe.local.flags.redirect_location = "/employee-portal"
		raise frappe.Redirect

	context.title = "Attendance Log | Setuware Technologies"
	context.no_cache = 1
	context.show_sidebar = False
