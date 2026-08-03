import frappe
from frappe.model.document import Document

class LMSEmployee(Document):
	def validate(self):
		if self.email:
			if not self.email.count("@") == 1:
				frappe.throw("Invalid email format")
		
		if self.joining_date:
			from datetime import datetime
			try:
				datetime.strptime(str(self.joining_date), "%Y-%m-%d")
			except ValueError:
				frappe.throw("Invalid date format. Use YYYY-MM-DD")
		
		if self.employee_id:
			existing = frappe.db.exists("LMS Employee", {"employee_id": self.employee_id, "name": ["!=", self.name]})
			if existing:
				frappe.throw(f"Employee ID {self.employee_id} already exists")
