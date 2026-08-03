import json

import frappe


def after_migrate():
	create_workspace()


def create_workspace():
	if frappe.db.exists("Workspace", "Employee Management"):
		return

	links = [
		{
			"type": "Card Break",
			"label": "HR Operations",
			"icon": "organization",
			"hidden": 0,
			"description": "Manage employees, leaves, attendance and tasks.",
		},
	]

	for doctype in ("LMS Employee", "LMS Leave Request", "LMS Attendance", "LMS Task"):
		links.append({
			"type": "Link",
			"label": doctype,
			"link_type": "DocType",
			"link_to": doctype,
			"onboard": 1,
			"hidden": 0,
			"is_query_report": 0,
		})

	links.append({
		"type": "Card Break",
		"label": "Website",
		"icon": "link",
		"hidden": 0,
		"description": (
			'<a href="/employee-portal" class="mr-2">My Portal</a>'
			'<a href="/employee-list" class="mr-2">Employee Directory</a>'
			'<a href="/attendance-log" class="mr-2">Attendance Log</a>'
			'<a href="/tasks">Tasks</a>'
		),
	})

	content = json.dumps([{
		"id": "lms-header",
		"type": "header",
		"data": {
			"text": "<span class=\"h4\">Employee Management & Leave Tracking</span>",
			"col": 12,
		},
	}])

	doc = frappe.get_doc({
		"doctype": "Workspace",
		"label": "Employee Management",
		"title": "Employee Management",
		"module": "LMS",
		"icon": "organization",
		"public": 1,
		"is_hidden": 0,
		"sequence_id": 1,
		"content": content,
		"links": links,
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
