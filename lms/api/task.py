import frappe
from frappe.utils import now_datetime, get_datetime, flt, cint

from lms.api.attendance import get_employee_for_user, is_admin


def _require_admin():
	if not is_admin():
		frappe.throw("You do not have permission to perform this action")


def _task_dict(doc):
	return {
		"name": doc.name,
		"task_id": doc.task_id,
		"title": doc.title,
		"description": doc.description,
		"assigned_to": doc.assigned_to,
		"assigned_by": doc.assigned_by,
		"priority": doc.priority,
		"status": doc.status,
		"due_date": str(doc.due_date) if doc.due_date else None,
		"estimated_hours": doc.estimated_hours,
		"total_time": doc.total_time,
		"timer_running": doc.timer_running,
		"notes": doc.notes,
		"timers": [
			{
				"started_at": str(t.started_at) if t.started_at else None,
				"ended_at": str(t.ended_at) if t.ended_at else None,
				"duration": t.duration
			}
			for t in doc.timers
		]
	}


@frappe.whitelist()
def get_tasks(status=None, assigned_to=None, search_term="", page=1, page_size=20):
	try:
		_require_admin()
		page = cint(page) or 1
		page_size = cint(page_size) or 20
		start = (page - 1) * page_size

		filters = {}
		if status:
			filters["status"] = status
		if assigned_to:
			filters["assigned_to"] = assigned_to
		if search_term:
			filters["title"] = ["like", f"%{search_term}%"]

		tasks = frappe.get_list(
			"LMS Task",
			fields=[
				"name", "task_id", "title", "assigned_to", "priority", "status",
				"due_date", "estimated_hours", "total_time", "timer_running"
			],
			filters=filters,
			order_by="modified desc",
			start=start,
			page_length=page_size
		)

		employees = {
			emp["name"]: emp
			for emp in frappe.get_all("LMS Employee", fields=["name", "full_name", "employee_id"])
		}

		for t in tasks:
			emp = employees.get(t.get("assigned_to")) or {}
			t["assigned_to_name"] = emp.get("full_name") or t.get("assigned_to") or "Unassigned"

		total = len(frappe.get_all("LMS Task", filters=filters))

		return {
			"success": True,
			"data": tasks,
			"total": total,
			"page": page,
			"total_pages": max(1, (total + page_size - 1) // page_size)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Tasks Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_my_tasks(status=None):
	try:
		emp = get_employee_for_user()
		if not emp:
			return {"success": False, "message": "No LMS Employee record linked to your account."}

		filters = {"assigned_to": emp}
		if status:
			filters["status"] = status

		tasks = frappe.get_all(
			"LMS Task",
			fields=[
				"name", "task_id", "title", "description", "priority", "status",
				"due_date", "estimated_hours", "total_time", "timer_running", "assigned_by"
			],
			filters=filters,
			order_by="modified desc"
		)

		return {"success": True, "data": tasks}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get My Tasks Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_task_detail(name):
	try:
		doc = frappe.get_doc("LMS Task", name)
		emp = get_employee_for_user()
		if not is_admin() and not (doc.assigned_to and doc.assigned_to == emp):
			frappe.throw("You can only view tasks assigned to you")
		return {"success": True, "data": _task_dict(doc)}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Task Detail Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def create_task(data):
	try:
		_require_admin()
		if isinstance(data, str):
			import json
			data = json.loads(data)

		if not data.get("title"):
			return {"success": False, "message": "Task title is required"}

		assigned_by = get_employee_for_user()

		doc = frappe.get_doc({
			"doctype": "LMS Task",
			"title": data.get("title"),
			"description": data.get("description"),
			"assigned_to": data.get("assigned_to"),
			"assigned_by": assigned_by,
			"priority": data.get("priority", "Medium"),
			"status": data.get("status", "Not Started"),
			"due_date": data.get("due_date"),
			"estimated_hours": data.get("estimated_hours"),
			"notes": data.get("notes")
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": f"Task {doc.task_id} created successfully",
			"data": _task_dict(doc)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Create Task Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def update_task(name, data):
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)

		doc = frappe.get_doc("LMS Task", name)
		emp = get_employee_for_user()

		allowed_status = {"Not Started", "In Progress", "Completed", "Cancelled"}
		changes = data.get("status") in allowed_status
		is_assignee = doc.assigned_to and doc.assigned_to == emp

		if not is_admin() and not is_assignee:
			frappe.throw("You do not have permission to update this task")

		if "title" in data:
			if not is_admin():
				frappe.throw("Only admins can change task details")
			doc.title = data["title"]
		if "description" in data and is_admin():
			doc.description = data["description"]
		if "assigned_to" in data:
			if not is_admin():
				frappe.throw("Only admins can reassign tasks")
			doc.assigned_to = data["assigned_to"]
		if "priority" in data:
			if not is_admin():
				frappe.throw("Only admins can change priority")
			doc.priority = data["priority"]
		if "due_date" in data and is_admin():
			doc.due_date = data["due_date"]
		if "estimated_hours" in data and is_admin():
			doc.estimated_hours = data["estimated_hours"]
		if "notes" in data and is_admin():
			doc.notes = data["notes"]
		if data.get("status") in allowed_status:
			doc.status = data["status"]

		doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": "Task updated successfully",
			"data": _task_dict(doc)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Update Task Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def delete_task(name):
	try:
		_require_admin()
		frappe.delete_doc("LMS Task", name, force=True)
		frappe.db.commit()
		return {"success": True, "message": "Task deleted"}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Delete Task Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def start_timer(task):
	try:
		emp = get_employee_for_user()
		doc = frappe.get_doc("LMS Task", task)

		is_assignee = doc.assigned_to and doc.assigned_to == emp
		if not is_admin() and not is_assignee:
			frappe.throw("You can only time-track tasks assigned to you")

		if doc.timer_running:
			return {"success": False, "message": "A timer is already running for this task"}

		open_timer = any(not t.ended_at for t in doc.timers)
		if open_timer:
			return {"success": False, "message": "A timer is already running for this task"}

		doc.append("timers", {
			"employee": emp,
			"started_at": now_datetime()
		})
		doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": "Timer started",
			"data": _task_dict(doc)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Start Timer Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def stop_timer(task):
	try:
		emp = get_employee_for_user()
		doc = frappe.get_doc("LMS Task", task)

		is_assignee = doc.assigned_to and doc.assigned_to == emp
		if not is_admin() and not is_assignee:
			frappe.throw("You can only time-track tasks assigned to you")

		now = now_datetime()
		stopped = False

		for timer in doc.timers:
			if not timer.ended_at:
				timer.ended_at = now
				timer.duration = flt((get_datetime(now) - get_datetime(timer.started_at)).total_seconds() / 3600, 2)
				stopped = True

		if not stopped:
			return {"success": False, "message": "No running timer for this task"}

		doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": f"Timer stopped. Total tracked time: {doc.total_time} hrs",
			"data": _task_dict(doc)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Stop Timer Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_task_summary():
	try:
		emp = get_employee_for_user()
		filters = {"assigned_to": emp} if emp and not is_admin() else {}

		tasks = frappe.get_all(
			"LMS Task",
			fields=["status", "total_time", "timer_running", "priority"],
			filters=filters
		)

		summary = {
			"total": len(tasks),
			"not_started": 0,
			"in_progress": 0,
			"completed": 0,
			"cancelled": 0,
			"total_hours": 0.0,
			"running_timer": False
		}

		for t in tasks:
			summary[t["status"].lower().replace(" ", "_")] = summary.get(t["status"].lower().replace(" ", "_"), 0) + 1
			summary["total_hours"] += t.get("total_time") or 0
			if t.get("timer_running"):
				summary["running_timer"] = True

		summary["total_hours"] = flt(summary["total_hours"], 2)
		return {"success": True, "data": summary}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Task Summary Error")
		return {"success": False, "message": str(e)}
