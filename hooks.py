from frappe import _

app_name = "lms"
app_title = "Employee Management & Leave Tracking"

app_include_js = [
	"/assets/lms/js/employee.js",
	"/assets/lms/js/leave_request.js"
]

app_include_css = [
	"/assets/lms/css/lms.css"
]

boot_session = "lms.boot.boot_session"

app_license = "MIT"

doc_events = {
	"Employee": {
		"validate": "lms.utils.employee.validate_employee"
	},
	"Leave Request": {
		"validate": "lms.utils.leave_request.validate_leave_request",
		"on_update": "lms.utils.leave_request.update_leave_status"
	}
}

website_route_rules = [
	{"from_route": "/employee-list", "to_route": "employee_list"}
]

permission_query_conditions = {
	"Employee": "lms.utils.employee.get_permission_query_conditions",
	"Leave Request": "lms.utils.leave_request.get_permission_query_conditions"
}

has_permission = {
	"Employee": "lms.utils.employee.has_permission",
	"Leave Request": "lms.utils.leave_request.has_permission"
}
