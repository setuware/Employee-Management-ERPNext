import frappe


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/employee-portal"
		raise frappe.Redirect

	context.title = "My Portal | Setuware Technologies"
	context.no_cache = 1
	context.show_sidebar = False
