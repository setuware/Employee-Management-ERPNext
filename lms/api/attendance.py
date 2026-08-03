import frappe
from frappe.utils import cint, flt, getdate, now_datetime, nowdate

from lms.api.auth import get_employee_for_user, require_admin


@frappe.whitelist()
def check_in():
	try:
		emp = get_employee_for_user()
		if not emp:
			return {
				"success": False,
				"message": "No LMS Employee record linked to your account. Contact your administrator.",
			}

		today = nowdate()
		existing = frappe.db.get_value(
			"LMS Attendance",
			{"employee": emp, "attendance_date": today},
			["name", "check_in"],
			as_dict=True,
		)

		if existing and existing.check_in:
			return {"success": False, "message": "You have already checked in today."}

		if existing:
			doc = frappe.get_doc("LMS Attendance", existing.name)
		else:
			doc = frappe.get_doc({
				"doctype": "LMS Attendance",
				"employee": emp,
				"attendance_date": today,
				"source": "Portal"
			})

		doc.check_in = now_datetime()
		doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": f"Checked in at {doc.check_in}",
			"data": _attendance_dict(doc)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Check In Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def check_out():
	try:
		emp = get_employee_for_user()
		if not emp:
			return {
				"success": False,
				"message": "No LMS Employee record linked to your account. Contact your administrator.",
			}

		today = nowdate()
		existing = frappe.db.get_value(
			"LMS Attendance",
			{"employee": emp, "attendance_date": today},
			["name", "check_in", "check_out"],
			as_dict=True,
		)

		if not existing or not existing.check_in:
			return {"success": False, "message": "You have not checked in today."}

		if existing.check_out:
			return {"success": False, "message": "You have already checked out today."}

		doc = frappe.get_doc("LMS Attendance", existing.name)
		doc.check_out = now_datetime()
		doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": f"Checked out at {doc.check_out}. Work hours: {doc.work_hours}",
			"data": _attendance_dict(doc)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Check Out Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_today():
	try:
		emp = get_employee_for_user()
		if not emp:
			return {"success": False, "message": "No LMS Employee record linked to your account."}

		att = frappe.db.get_value(
			"LMS Attendance",
			{"employee": emp, "attendance_date": nowdate()},
			as_dict=True,
		)

		if not att:
			return {"success": True, "data": None}

		doc = frappe.get_doc("LMS Attendance", att.name)
		return {"success": True, "data": _attendance_dict(doc)}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Today Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_my_attendance(month=None, page=1, page_size=15):
	try:
		emp = get_employee_for_user()
		if not emp:
			return {"success": False, "message": "No LMS Employee record linked to your account."}

		page = cint(page) or 1
		page_size = cint(page_size) or 15
		start = (page - 1) * page_size

		filters = {"employee": emp}
		if month:
			from frappe.utils import get_first_day, get_last_day, getdate

			month_date = getdate(f"{month}-01")
			filters["attendance_date"] = ["between", [get_first_day(month_date), get_last_day(month_date)]]

		records = frappe.get_list(
			"LMS Attendance",
			fields=["name", "attendance_date", "check_in", "check_out", "work_hours", "status", "notes"],
			filters=filters,
			order_by="attendance_date desc",
			start=start,
			page_length=page_size
		)

		total = len(frappe.get_all("LMS Attendance", filters=filters))

		return {
			"success": True,
			"data": records,
			"total": total,
			"page": page,
			"total_pages": max(1, (total + page_size - 1) // page_size)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get My Attendance Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_attendance_log(date=None, employee=None, status=None, page=1, page_size=20):
	try:
		require_admin()
		page = cint(page) or 1
		page_size = cint(page_size) or 20
		start = (page - 1) * page_size

		filters = {}
		if date:
			filters["attendance_date"] = date
		if employee:
			filters["employee"] = employee
		if status:
			filters["status"] = status

		records = frappe.get_list(
			"LMS Attendance",
			fields=[
				"name", "employee", "attendance_date", "check_in", "check_out",
				"work_hours", "status", "source", "notes",
			],
			filters=filters,
			order_by="attendance_date desc, creation desc",
			start=start,
			page_length=page_size
		)

		employees = {
			emp["name"]: emp
			for emp in frappe.get_all("LMS Employee", fields=["name", "full_name", "employee_id"])
		}

		for rec in records:
			emp = employees.get(rec.get("employee")) or {}
			rec["employee_name"] = emp.get("full_name") or rec.get("employee")
			rec["employee_id"] = emp.get("employee_id") or ""

		total = len(frappe.get_all("LMS Attendance", filters=filters))

		return {
			"success": True,
			"data": records,
			"total": total,
			"page": page,
			"total_pages": max(1, (total + page_size - 1) // page_size)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Attendance Log Error")
		return {"success": False, "message": str(e)}


def _clean_dt(value):
	if not value:
		return None
	return str(value).replace("T", " ")


@frappe.whitelist()
def record_attendance(data):
	try:
		require_admin()
		if isinstance(data, str):
			import json
			data = json.loads(data)

		if not data.get("employee") or not data.get("attendance_date"):
			return {"success": False, "message": "Employee and date are required"}

		existing = frappe.db.get_value(
			"LMS Attendance",
			{"employee": data["employee"], "attendance_date": data["attendance_date"]},
			"name",
		)

		if existing:
			doc = frappe.get_doc("LMS Attendance", existing)
		else:
			doc = frappe.get_doc({
				"doctype": "LMS Attendance",
				"employee": data["employee"],
				"attendance_date": data["attendance_date"],
				"source": "Admin"
			})

		if "check_in" in data:
			doc.check_in = _clean_dt(data["check_in"])
		if "check_out" in data:
			doc.check_out = _clean_dt(data["check_out"])
		if "status" in data:
			doc.status = data["status"]
		if "notes" in data:
			doc.notes = data["notes"]

		doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": "Attendance recorded successfully",
			"data": _attendance_dict(doc)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Record Attendance Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def delete_attendance(name):
	try:
		require_admin()
		frappe.delete_doc("LMS Attendance", name, force=True)
		frappe.db.commit()
		return {"success": True, "message": "Attendance record deleted"}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Delete Attendance Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_attendance_summary(date=None):
	try:
		require_admin()
		date = date or nowdate()
		records = frappe.get_all(
			"LMS Attendance",
			fields=["employee", "status", "work_hours", "check_in"],
			filters={"attendance_date": date}
		)

		total_employees = frappe.db.count("LMS Employee")
		present = [r for r in records if r["check_in"]]
		status_counts = {}
		total_hours = 0.0
		for r in records:
			status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
			total_hours += r.get("work_hours") or 0

		return {
			"success": True,
			"data": {
				"date": date,
				"total_employees": total_employees,
				"checked_in": len(present),
				"absent": max(0, total_employees - len(present)),
				"status_counts": status_counts,
				"total_hours": flt(total_hours, 2)
			}
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Attendance Summary Error")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_my_summary():
	try:
		emp = get_employee_for_user()
		if not emp:
			return {"success": False, "message": "No LMS Employee record linked to your account."}

		today = nowdate()
		month_start = getdate(today).replace(day=1)

		this_month = frappe.get_all(
			"LMS Attendance",
			fields=["status", "work_hours", "check_in"],
			filters={
				"employee": emp,
				"attendance_date": ["between", [month_start, today]]
			}
		)

		present_days = 0
		total_hours = 0.0
		lates = 0
		for r in this_month:
			if r.get("check_in"):
				present_days += 1
			if r.get("work_hours"):
				total_hours += r["work_hours"]
			if r.get("status") == "Late":
				lates += 1

		today_att = frappe.db.get_value(
			"LMS Attendance",
			{"employee": emp, "attendance_date": today},
			["status", "check_in", "check_out", "work_hours"],
			as_dict=True,
		)

		return {
			"success": True,
			"data": {
				"month": str(month_start)[:7],
				"present_days": present_days,
				"total_hours": flt(total_hours, 2),
				"lates": lates,
				"today": today_att or None
			}
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get My Summary Error")
		return {"success": False, "message": str(e)}


def _attendance_dict(doc):
	return {
		"name": doc.name,
		"employee": doc.employee,
		"attendance_date": str(doc.attendance_date),
		"check_in": str(doc.check_in) if doc.check_in else None,
		"check_out": str(doc.check_out) if doc.check_out else None,
		"work_hours": doc.work_hours,
		"status": doc.status,
		"source": doc.source,
		"notes": doc.notes
	}
