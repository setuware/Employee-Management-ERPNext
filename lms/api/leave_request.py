import frappe
from frappe.utils import cint

from lms.api.auth import get_employee_for_user, is_admin, require_admin


@frappe.whitelist()
def get_leave_requests(page=1, page_size=10, search_term="", status=""):
	try:
		require_admin()
		page = cint(page) or 1
		page_size = cint(page_size) or 10
		start = (page - 1) * page_size

		filters = {}
		if search_term:
			filters["or"] = [
				["leave_id", "like", f"%{search_term}%"],
				["employee", "like", f"%{search_term}%"],
				["leave_type", "like", f"%{search_term}%"]
			]
		if status:
			filters["status"] = status

		leave_requests = frappe.get_list(
			"LMS Leave Request",
			fields=["name", "leave_id", "employee", "leave_type", "from_date", "to_date", "status"],
			filters=filters,
			order_by="modified desc",
			start=start,
			page_length=page_size
		)

		for lr in leave_requests:
			if lr.get("employee"):
				emp = frappe.get_doc("LMS Employee", lr["employee"])
				lr["employee_name"] = emp.full_name
				lr["employee_profile"] = emp.profile_picture
				lr["employee_email"] = emp.email

		total_count = len(frappe.get_all("LMS Leave Request", filters=filters))

		return {
			"success": True,
			"data": leave_requests,
			"total": total_count,
			"page": page,
			"page_size": page_size,
			"total_pages": (total_count + page_size - 1) // page_size
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Leave Requests Error")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def create_leave_request(data):
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)

		if not is_admin():
			emp = get_employee_for_user()
			if not emp:
				return {
					"success": False,
					"message": "No LMS Employee record linked to your account. Contact your administrator."
				}
			data["employee"] = emp
			data["status"] = "Pending"

		if not data.get("employee"):
			return {"success": False, "message": "Employee is required"}

		doc = frappe.get_doc({
			"doctype": "LMS Leave Request",
			"employee": data.get("employee"),
			"leave_type": data.get("leave_type"),
			"from_date": data.get("from_date"),
			"to_date": data.get("to_date"),
			"status": data.get("status", "Pending")
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": "Leave request created successfully",
			"data": doc.as_dict()
		}
	except frappe.ValidationError as e:
		return {"success": False, "message": str(e)}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Create Leave Request Error")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def update_leave_request(name, data):
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)

		doc = frappe.get_doc("LMS Leave Request", name)

		if not is_admin():
			emp = get_employee_for_user()
			if not emp or doc.employee != emp:
				frappe.throw("You do not have permission to update this request")
			if doc.status != "Pending":
				frappe.throw("Only pending requests can be edited")
			if "status" in data and data["status"] != "Canceled":
				frappe.throw("Only administrators can change the status")

		if "employee" in data and is_admin():
			doc.employee = data["employee"]
		if "leave_type" in data:
			doc.leave_type = data["leave_type"]
		if "from_date" in data:
			doc.from_date = data["from_date"]
		if "to_date" in data:
			doc.to_date = data["to_date"]
		if "status" in data:
			doc.status = data["status"]

		doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": "Leave request updated successfully",
			"data": doc.as_dict()
		}
	except frappe.ValidationError as e:
		return {"success": False, "message": str(e)}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Update Leave Request Error")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_leave_request(name):
	try:
		doc = frappe.get_doc("LMS Leave Request", name)
		if not is_admin() and get_employee_for_user() != doc.employee:
			frappe.throw("You do not have permission to view this request")
		data = doc.as_dict()

		if data.get("employee"):
			emp = frappe.get_doc("LMS Employee", data["employee"])
			data["employee_name"] = emp.full_name
			data["employee_profile"] = emp.profile_picture
			data["employee_email"] = emp.email

		return {
			"success": True,
			"data": data
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Leave Request Error")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_my_leave_requests(page=1, page_size=10, status=""):
	try:
		emp = get_employee_for_user()
		if not emp:
			return {
				"success": False,
				"message": "No LMS Employee record linked to your account. Contact your administrator."
			}

		page = cint(page) or 1
		page_size = cint(page_size) or 10
		start = (page - 1) * page_size

		filters = {"employee": emp}
		if status:
			filters["status"] = status

		requests = frappe.get_list(
			"LMS Leave Request",
			fields=["name", "leave_id", "leave_type", "from_date", "to_date", "status"],
			filters=filters,
			order_by="modified desc",
			start=start,
			page_length=page_size
		)

		total = len(frappe.get_all("LMS Leave Request", filters=filters))

		return {
			"success": True,
			"data": requests,
			"total": total,
			"page": page,
			"total_pages": max(1, (total + page_size - 1) // page_size)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get My Leave Requests Error")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_summary():
	try:
		require_admin()
		total = frappe.db.count("LMS Leave Request")
		approved = frappe.db.count("LMS Leave Request", {"status": "Approved"})
		pending = frappe.db.count("LMS Leave Request", {"status": "Pending"})
		canceled = frappe.db.count("LMS Leave Request", {"status": "Canceled"})
		rejected = frappe.db.count("LMS Leave Request", {"status": "Rejected"})

		return {
			"success": True,
			"data": {
				"total_leaves": total,
				"approved_leaves": approved,
				"pending_leaves": pending,
				"canceled_leaves": canceled,
				"rejected_leaves": rejected
			}
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Summary Error")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def export_csv():
	try:
		require_admin()
		import csv
		from io import StringIO

		from frappe.utils import now_datetime

		leave_requests = frappe.get_all(
			"LMS Leave Request",
			fields=["leave_id", "employee", "leave_type", "from_date", "to_date", "status"],
			order_by="modified desc"
		)

		for lr in leave_requests:
			if lr.get("employee"):
				try:
					emp = frappe.get_doc("LMS Employee", lr["employee"])
					lr["employee_name"] = emp.full_name
					lr["employee_email"] = emp.email
				except frappe.DoesNotExistError:
					lr["employee_name"] = ""
					lr["employee_email"] = ""

		output = StringIO()
		fieldnames = ['leave_id', 'employee_name', 'employee_email', 'leave_type', 'from_date', 'to_date', 'status']
		writer = csv.DictWriter(output, fieldnames=fieldnames)
		writer.writeheader()

		for lr in leave_requests:
			writer.writerow({
				'leave_id': lr.get('leave_id', ''),
				'employee_name': lr.get('employee_name', ''),
				'employee_email': lr.get('employee_email', ''),
				'leave_type': lr.get('leave_type', ''),
				'from_date': str(lr.get('from_date', '')),
				'to_date': str(lr.get('to_date', '')),
				'status': lr.get('status', '')
			})

		csv_content = output.getvalue()
		output.close()

		timestamp = now_datetime().strftime("%Y%m%d_%H%M%S")
		file_name = f"leave_summary_{timestamp}.csv"

		file_doc = frappe.get_doc({
			"doctype": "File",
			"file_name": file_name,
			"content": csv_content,
			"is_private": 0
		})
		file_doc.save()
		frappe.db.commit()

		return {
			"success": True,
			"message": "CSV exported successfully",
			"file_url": file_doc.file_url,
			"file_name": file_doc.file_name
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Export CSV Error")
		return {"success": False, "message": str(e)}
