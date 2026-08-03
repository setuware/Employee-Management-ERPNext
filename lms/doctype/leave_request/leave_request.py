import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime

class LeaveRequest(Document):
	def before_insert(self):
		if not self.leave_id:
			self.leave_id = self.generate_leave_id()
	
	def generate_leave_id(self):
		from datetime import datetime
		timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
		return f"LR{timestamp}"
	
	def validate(self):
		if self.from_date and self.to_date:
			if self.to_date < self.from_date:
				frappe.throw("To Date cannot be before From Date")
		
		if self.employee:
			employee_exists = frappe.db.exists("Employee", self.employee)
			if not employee_exists:
				frappe.throw(f"Employee {self.employee} does not exist")
		
		if self.status not in ["Pending", "Approved", "Rejected", "Canceled"]:
			frappe.throw("Invalid status. Must be Pending, Approved, Rejected, or Canceled")
	
	def on_update(self):
		if self.has_value_changed("status"):
			self.update_employee_leave_count()
	
	def update_employee_leave_count(self):
		pass
