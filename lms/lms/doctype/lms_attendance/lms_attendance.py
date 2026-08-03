import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_datetime

WORK_START = (10, 0)
WORK_END = (17, 0)


class LMSAttendance(Document):
	def validate(self):
		if self.check_in and self.check_out:
			if get_datetime(self.check_out) < get_datetime(self.check_in):
				frappe.throw("Check Out cannot be before Check In")

		if self.source == "Portal" and frappe.session.user != "Administrator":
			linked = frappe.db.get_value("LMS Employee", {"user": frappe.session.user})
			if not linked or linked != self.employee:
				frappe.throw("You can only record your own attendance")

		self.work_hours = 0.0
		if self.check_in and self.check_out:
			self.work_hours = flt(
				(get_datetime(self.check_out) - get_datetime(self.check_in)).total_seconds() / 3600,
				2,
			)

		if self.source == "Portal":
			self.auto_status()

	def auto_status(self):
		if self.check_in and self.check_out:
			ci = get_datetime(self.check_in).time()
			co = get_datetime(self.check_out).time()
			late = (ci.hour, ci.minute) > WORK_START
			early = (co.hour, co.minute) < WORK_END

			if late and early:
				self.status = "Half Day"
			elif late:
				self.status = "Late"
			elif early:
				self.status = "Early Leave"
			else:
				self.status = "Present"
		elif self.check_in:
			self.status = "Present"
