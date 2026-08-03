import frappe
from frappe import _
from frappe.utils import cint

@frappe.whitelist()
def get_employees(page=1, page_size=10, search_term=""):
	try:
		page = cint(page) or 1
		page_size = cint(page_size) or 10
		start = (page - 1) * page_size
		
		filters = {}
		if search_term:
			filters = {
				"or": [
					["employee_id", "like", f"%{search_term}%"],
					["full_name", "like", f"%{search_term}%"],
					["email", "like", f"%{search_term}%"],
					["department", "like", f"%{search_term}%"]
				]
			}
		
		employees = frappe.get_list(
			"Employee",
			fields=["name", "employee_id", "profile_picture", "full_name", "email", "department", "joining_date"],
			filters=filters,
			order_by="modified desc",
			start=start,
			page_length=page_size
		)
		
		total_count = frappe.db.count("Employee", filters=filters)
		
		return {
			"success": True,
			"data": employees,
			"total": total_count,
			"page": page,
			"page_size": page_size,
			"total_pages": (total_count + page_size - 1) // page_size
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Employees Error")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def create_employee(data):
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)
		
		doc = frappe.get_doc({
			"doctype": "Employee",
			"employee_id": data.get("employee_id"),
			"profile_picture": data.get("profile_picture"),
			"full_name": data.get("full_name"),
			"email": data.get("email"),
			"department": data.get("department"),
			"joining_date": data.get("joining_date")
		})
		doc.insert()
		frappe.db.commit()
		
		return {
			"success": True,
			"message": "Employee created successfully",
			"data": doc.as_dict()
		}
	except frappe.ValidationError as e:
		return {"success": False, "message": str(e)}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Create Employee Error")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def update_employee(name, data):
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)
		
		doc = frappe.get_doc("Employee", name)
		
		if "employee_id" in data:
			doc.employee_id = data["employee_id"]
		if "profile_picture" in data:
			doc.profile_picture = data["profile_picture"]
		if "full_name" in data:
			doc.full_name = data["full_name"]
		if "email" in data:
			doc.email = data["email"]
		if "department" in data:
			doc.department = data["department"]
		if "joining_date" in data:
			doc.joining_date = data["joining_date"]
		
		doc.save()
		frappe.db.commit()
		
		return {
			"success": True,
			"message": "Employee updated successfully",
			"data": doc.as_dict()
		}
	except frappe.ValidationError as e:
		return {"success": False, "message": str(e)}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Update Employee Error")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_employee(name):
	try:
		doc = frappe.get_doc("Employee", name)
		return {
			"success": True,
			"data": doc.as_dict()
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Employee Error")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def delete_employee(name):
	try:
		frappe.delete_doc("Employee", name)
		frappe.db.commit()
		return {
			"success": True,
			"message": "Employee deleted successfully"
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Delete Employee Error")
		return {"success": False, "message": str(e)}
