from frappe import _

app_name = "lms"
app_title = "Employee Management & Leave Tracking"
app_publisher = "Bits and Volts Pvt. Ltd."
app_description = "Employee Management & Leave Tracking module for ERPNext"
app_version = "0.0.1"

app_include_js = [
	"/assets/lms/js/employee.js",
	"/assets/lms/js/leave_request.js"
]

app_include_css = [
	"/assets/lms/css/lms.css"
]

boot_session = "lms.boot.boot_session"

app_license = "MIT"

website_route_rules = [
	{"from_route": "/employee-list", "to_route": "employee_list"}
]
