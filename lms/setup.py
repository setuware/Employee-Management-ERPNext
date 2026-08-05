import json

import frappe


def after_migrate():
	create_number_cards()
	create_charts()
	create_workspace()


def create_number_cards():
	cards = (
		{
			"label": "Total Employees",
			"document_type": "LMS Employee",
			"function": "Count",
			"color": "blue",
		},
		{
			"label": "Pending Leave Requests",
			"document_type": "LMS Leave Request",
			"function": "Count",
			"filters_json": json.dumps({"status": "Pending"}),
			"color": "orange",
		},
		{
			"label": "Approved Leave Requests",
			"document_type": "LMS Leave Request",
			"function": "Count",
			"filters_json": json.dumps({"status": "Approved"}),
			"color": "green",
		},
		{
			"label": "Open Tasks",
			"document_type": "LMS Task",
			"function": "Count",
			"filters_json": json.dumps({"status": ["in", ["Not Started", "In Progress"]]}),
			"color": "purple",
		},
	)
	for card in cards:
		if frappe.db.exists("Number Card", card["label"]):
			continue
		doc = frappe.get_doc({
			"doctype": "Number Card",
			"label": card["label"],
			"document_type": card["document_type"],
			"function": card["function"],
			"filters_json": card.get("filters_json"),
			"color": card["color"],
			"is_public": 1,
			"type": "Document Type",
			"module": "LMS",
		})
		doc.insert(ignore_permissions=True)
	frappe.db.commit()


def create_charts():
	charts = (
		{
			"label": "Employees by Department",
			"chart_type": "Group By",
			"document_type": "LMS Employee",
			"group_by_based_on": "department",
			"group_by_type": "Count",
			"type": "Bar",
		},
		{
			"label": "Leave Requests by Status",
			"chart_type": "Group By",
			"document_type": "LMS Leave Request",
			"group_by_based_on": "status",
			"group_by_type": "Count",
			"type": "Donut",
		},
		{
			"label": "Attendance Trend",
			"chart_type": "Count",
			"document_type": "LMS Attendance",
			"based_on": "attendance_date",
			"timespan": "Last Month",
			"time_interval": "Daily",
			"timeseries": 1,
			"type": "Line",
		},
	)
	for chart in charts:
		if frappe.db.exists("Dashboard Chart", chart["label"]):
			continue
		doc = frappe.get_doc({
			"doctype": "Dashboard Chart",
			"chart_name": chart["label"],
			"chart_type": chart["chart_type"],
			"document_type": chart["document_type"],
			"group_by_based_on": chart.get("group_by_based_on"),
			"group_by_type": chart.get("group_by_type"),
			"based_on": chart.get("based_on"),
			"timespan": chart.get("timespan"),
			"time_interval": chart.get("time_interval"),
			"timeseries": chart.get("timeseries", 0),
			"type": chart["type"],
			"is_public": 1,
			"module": "LMS",
		})
		doc.insert(ignore_permissions=True)
	frappe.db.commit()


def _sc(label, doctype, doc_view, color, icon, link_to=None, url=None):
	row = {
		"label": label,
		"type": "URL" if url else "DocType",
		"color": color,
		"icon": icon,
	}
	if url:
		row["url"] = url
	else:
		row["link_to"] = link_to or doctype
		row["doc_view"] = doc_view
	return row


def create_workspace():
	shortcuts = [
		_sc("New Employee", "LMS Employee", "New", "blue", "user"),
		_sc("Employee Directory", "LMS Employee", "List", "cyan", "users"),
		_sc("New Leave Request", "LMS Leave Request", "New", "orange", "file"),
		_sc("Leave Requests", "LMS Leave Request", "List", "orange", "filter"),
		_sc("Mark Attendance", "LMS Attendance", "New", "green", "check"),
		_sc("Attendance Log", "LMS Attendance", "List", "green", "calendar"),
		_sc("New Task", "LMS Task", "New", "purple", "task"),
		_sc("Task List", "LMS Task", "List", "purple", "list"),
		_sc("Employee Portal", None, None, "teal", "globe", url="/employee-portal"),
		_sc("Web Admin Dashboard", None, None, "teal", "settings", url="/employee-list"),
	]

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
			'<a href="/work-tasks" class="mr-2">Tasks</a>'
		),
	})

	content = json.dumps([
		{"type": "header", "data": {"text": "<span class=\"h4\">HR Overview</span>", "col": 12}},
		{"type": "number_card", "data": {"number_card_name": "Total Employees", "col": 3}},
		{"type": "number_card", "data": {"number_card_name": "Pending Leave Requests", "col": 3}},
		{"type": "number_card", "data": {"number_card_name": "Approved Leave Requests", "col": 3}},
		{"type": "number_card", "data": {"number_card_name": "Open Tasks", "col": 3}},
		{"type": "chart", "data": {"chart_name": "Employees by Department", "col": 6}},
		{"type": "chart", "data": {"chart_name": "Leave Requests by Status", "col": 6}},
		{"type": "spacer", "data": {"col": 12}},
		{"type": "header", "data": {"text": "<span class=\"h4\">Quick Actions</span>", "col": 12}},
		{"type": "shortcut", "data": {"shortcut_name": "New Employee", "col": 3}},
		{"type": "shortcut", "data": {"shortcut_name": "New Leave Request", "col": 3}},
		{"type": "shortcut", "data": {"shortcut_name": "Mark Attendance", "col": 3}},
		{"type": "shortcut", "data": {"shortcut_name": "New Task", "col": 3}},
		{"type": "shortcut", "data": {"shortcut_name": "Employee Directory", "col": 3}},
		{"type": "shortcut", "data": {"shortcut_name": "Leave Requests", "col": 3}},
		{"type": "shortcut", "data": {"shortcut_name": "Attendance Log", "col": 3}},
		{"type": "shortcut", "data": {"shortcut_name": "Task List", "col": 3}},
		{"type": "shortcut", "data": {"shortcut_name": "Employee Portal", "col": 3}},
		{"type": "shortcut", "data": {"shortcut_name": "Web Admin Dashboard", "col": 3}},
	])

	doc = None
	if frappe.db.exists("Workspace", "Employee Management"):
		doc = frappe.get_doc("Workspace", "Employee Management")
	else:
		doc = frappe.get_doc({"doctype": "Workspace", "label": "Employee Management"})

	doc.title = "Employee Management"
	doc.module = "LMS"
	doc.icon = "organization"
	doc.public = 1
	doc.is_hidden = 0
	doc.sequence_id = 1
	doc.content = content
	doc.shortcuts = shortcuts
	doc.number_cards = [
		{"label": label, "number_card_name": label}
		for label in ("Total Employees", "Pending Leave Requests", "Approved Leave Requests", "Open Tasks")
	]
	doc.charts = [
		{"label": label, "chart_name": label}
		for label in ("Employees by Department", "Leave Requests by Status", "Attendance Trend")
	]
	doc.links = links
	doc.save(ignore_permissions=True)
	frappe.db.commit()
