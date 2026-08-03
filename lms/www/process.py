import frappe

from lms.api.auth import is_admin


def get_context(context):
	context.title = "How We Work | Setuware Technologies"
	context.no_cache = 1
	context.show_sidebar = False
	context.logged_in = frappe.session.user != "Guest"
	context.is_admin = is_admin()
