import frappe

from lms.api.auth import is_admin


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/employee-portal"
		raise frappe.Redirect

	context.title = "My Portal | Setuware Technologies"
	context.no_cache = 1
	context.show_sidebar = False
	context.logged_in = True
	context.is_admin = is_admin()
