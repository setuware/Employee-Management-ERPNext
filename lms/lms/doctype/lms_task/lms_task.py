import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, flt, get_datetime, getdate, now_datetime


class LMSTask(Document):
	def before_insert(self):
		if not self.task_id:
			self.task_id = f"TSK{now_datetime().strftime('%Y%m%d%H%M%S%f')}"

	def validate(self):
		if self.due_date and date_diff(self.due_date, getdate()) < 0:
			frappe.throw("Due Date cannot be in the past")

		total = 0.0
		running = False

		for timer in self.timers:
			if timer.ended_at and timer.started_at:
				timer.duration = flt(
					(get_datetime(timer.ended_at) - get_datetime(timer.started_at)).total_seconds() / 3600,
					2,
				)
				total += timer.duration
			elif timer.started_at:
				running = True
				total += flt(
					(now_datetime() - get_datetime(timer.started_at)).total_seconds() / 3600,
					2,
				)

		self.total_time = flt(total, 2)
		self.timer_running = 1 if running else 0

		if running and self.status == "Not Started":
			self.status = "In Progress"
