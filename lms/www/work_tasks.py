import frappe

from lms.api.auth import is_admin


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/work-tasks"
		raise frappe.Redirect

	if not is_admin():
		frappe.local.flags.redirect_location = "/employee-portal"
		raise frappe.Redirect

	context.title = "Tasks | Setuware Technologies"
	context.no_cache = 1
	context.show_sidebar = False
	context.logged_in = True
	context.is_admin = True
