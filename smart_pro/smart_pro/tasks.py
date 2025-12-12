# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days, getdate, formatdate


def get_settings():
	"""Get Smart Pro Settings singleton"""
	try:
		return frappe.get_single("Smart Pro Settings")
	except Exception:
		return None


def is_email_notifications_enabled():
	"""Check if email notifications are enabled"""
	settings = get_settings()
	return settings and settings.enable_email_notifications


def send_project_end_date_reminders():
	"""
	Daily task: Send reminder emails to project managers when project end date is approaching or reached.
	Triggered when Enable Email Notifications is enabled in Smart Pro Settings.
	"""
	if not is_email_notifications_enabled():
		frappe.logger().info("Smart Pro: Email notifications disabled, skipping project end date reminders")
		return

	settings = get_settings()
	reminder_days = getattr(settings, "project_reminder_days", 3) or 3

	today_date = getdate(today())
	reminder_date = getdate(add_days(today(), reminder_days))

	# Get projects that are ending soon or have ended (not completed/cancelled)
	projects = frappe.get_all(
		"Smart Project",
		filters={
			"status": ["in", ["Planning", "Active", "On Hold"]],
			"end_date": ["<=", reminder_date],
			"end_date": ["is", "set"],
			"project_manager": ["is", "set"]
		},
		fields=["name", "title", "end_date", "project_manager", "status"]
	)

	if not projects:
		frappe.logger().info("Smart Pro: No projects approaching end date")
		return

	for project in projects:
		end_date = getdate(project.end_date)
		days_remaining = (end_date - today_date).days

		# Determine urgency
		if days_remaining < 0:
			urgency = "OVERDUE"
			urgency_message = f"This project is {abs(days_remaining)} day(s) overdue."
		elif days_remaining == 0:
			urgency = "DUE TODAY"
			urgency_message = "This project is due today!"
		else:
			urgency = "REMINDER"
			urgency_message = f"This project is due in {days_remaining} day(s)."

		# Check if we already sent a notification today for this project
		existing_log = frappe.db.exists(
			"Communication",
			{
				"reference_doctype": "Smart Project",
				"reference_name": project.name,
				"communication_date": today(),
				"subject": ["like", f"%{urgency}%"]
			}
		)

		if existing_log:
			continue

		# Send email to project manager
		try:
			subject = f"[{urgency}] Project End Date: {project.title}"
			message = f"""
			<h3>Project End Date {urgency}</h3>
			<p>{urgency_message}</p>
			<table style="border-collapse: collapse; width: 100%; max-width: 500px;">
				<tr>
					<td style="padding: 8px; border: 1px solid #ddd;"><strong>Project</strong></td>
					<td style="padding: 8px; border: 1px solid #ddd;">{project.title}</td>
				</tr>
				<tr>
					<td style="padding: 8px; border: 1px solid #ddd;"><strong>End Date</strong></td>
					<td style="padding: 8px; border: 1px solid #ddd;">{formatdate(project.end_date)}</td>
				</tr>
				<tr>
					<td style="padding: 8px; border: 1px solid #ddd;"><strong>Status</strong></td>
					<td style="padding: 8px; border: 1px solid #ddd;">{project.status}</td>
				</tr>
			</table>
			<p style="margin-top: 16px;">
				<a href="{frappe.utils.get_url()}/app/smart-project/{project.name}"
				   style="background-color: #5e64ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
					View Project
				</a>
			</p>
			<p style="color: #666; font-size: 12px; margin-top: 20px;">
				This is an automated reminder from Smart Pro.
			</p>
			"""

			frappe.sendmail(
				recipients=[project.project_manager],
				subject=subject,
				message=message,
				reference_doctype="Smart Project",
				reference_name=project.name,
				now=True
			)

			frappe.logger().info(f"Smart Pro: Sent project end date reminder for {project.name} to {project.project_manager}")

		except Exception as e:
			frappe.logger().error(f"Smart Pro: Error sending project reminder for {project.name}: {str(e)}")


def send_task_due_date_reminders():
	"""
	Daily task: Send reminder emails to assigned employees when task due date is approaching or reached.
	Triggered when Enable Email Notifications is enabled in Smart Pro Settings.
	"""
	if not is_email_notifications_enabled():
		frappe.logger().info("Smart Pro: Email notifications disabled, skipping task due date reminders")
		return

	settings = get_settings()
	reminder_days = getattr(settings, "task_reminder_days", 2) or 2

	today_date = getdate(today())
	reminder_date = getdate(add_days(today(), reminder_days))

	# Get tasks that are due soon or overdue (not completed/cancelled)
	tasks = frappe.get_all(
		"Smart Task",
		filters={
			"status": ["in", ["Open", "Working", "Pending Review"]],
			"due_date": ["<=", reminder_date],
			"due_date": ["is", "set"],
			"assigned_to": ["is", "set"]
		},
		fields=["name", "title", "due_date", "assigned_to", "status", "priority", "project"]
	)

	if not tasks:
		frappe.logger().info("Smart Pro: No tasks approaching due date")
		return

	for task in tasks:
		due_date = getdate(task.due_date)
		days_remaining = (due_date - today_date).days

		# Determine urgency
		if days_remaining < 0:
			urgency = "OVERDUE"
			urgency_message = f"This task is {abs(days_remaining)} day(s) overdue."
		elif days_remaining == 0:
			urgency = "DUE TODAY"
			urgency_message = "This task is due today!"
		else:
			urgency = "REMINDER"
			urgency_message = f"This task is due in {days_remaining} day(s)."

		# Check if we already sent a notification today for this task
		existing_log = frappe.db.exists(
			"Communication",
			{
				"reference_doctype": "Smart Task",
				"reference_name": task.name,
				"communication_date": today(),
				"subject": ["like", f"%{urgency}%"]
			}
		)

		if existing_log:
			continue

		# Get project title if available
		project_title = ""
		if task.project:
			project_doc = frappe.db.get_value("Smart Project", task.project, "title")
			project_title = project_doc or task.project

		# Send email to assigned employee
		try:
			subject = f"[{urgency}] Task Due: {task.title}"
			message = f"""
			<h3>Task Due Date {urgency}</h3>
			<p>{urgency_message}</p>
			<table style="border-collapse: collapse; width: 100%; max-width: 500px;">
				<tr>
					<td style="padding: 8px; border: 1px solid #ddd;"><strong>Task</strong></td>
					<td style="padding: 8px; border: 1px solid #ddd;">{task.title}</td>
				</tr>
				<tr>
					<td style="padding: 8px; border: 1px solid #ddd;"><strong>Due Date</strong></td>
					<td style="padding: 8px; border: 1px solid #ddd;">{formatdate(task.due_date)}</td>
				</tr>
				<tr>
					<td style="padding: 8px; border: 1px solid #ddd;"><strong>Priority</strong></td>
					<td style="padding: 8px; border: 1px solid #ddd;">{task.priority}</td>
				</tr>
				<tr>
					<td style="padding: 8px; border: 1px solid #ddd;"><strong>Status</strong></td>
					<td style="padding: 8px; border: 1px solid #ddd;">{task.status}</td>
				</tr>
				{f'<tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Project</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{project_title}</td></tr>' if project_title else ''}
			</table>
			<p style="margin-top: 16px;">
				<a href="{frappe.utils.get_url()}/app/smart-task/{task.name}"
				   style="background-color: #5e64ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
					View Task
				</a>
			</p>
			<p style="color: #666; font-size: 12px; margin-top: 20px;">
				This is an automated reminder from Smart Pro.
			</p>
			"""

			frappe.sendmail(
				recipients=[task.assigned_to],
				subject=subject,
				message=message,
				reference_doctype="Smart Task",
				reference_name=task.name,
				now=True
			)

			frappe.logger().info(f"Smart Pro: Sent task due date reminder for {task.name} to {task.assigned_to}")

		except Exception as e:
			frappe.logger().error(f"Smart Pro: Error sending task reminder for {task.name}: {str(e)}")


def send_weekly_project_report():
	"""
	Weekly task: Send project status report to all project managers.
	Triggered when Enable Email Notifications is enabled in Smart Pro Settings.
	"""
	if not is_email_notifications_enabled():
		frappe.logger().info("Smart Pro: Email notifications disabled, skipping weekly report")
		return

	# Get all active project managers
	project_managers = frappe.db.sql("""
		SELECT DISTINCT project_manager
		FROM `tabSmart Project`
		WHERE status IN ('Planning', 'Active', 'On Hold')
		AND project_manager IS NOT NULL
		AND project_manager != ''
	""", as_dict=True)

	if not project_managers:
		frappe.logger().info("Smart Pro: No project managers found for weekly report")
		return

	today_date = getdate(today())

	for pm in project_managers:
		manager_email = pm.project_manager

		# Get all projects for this manager
		projects = frappe.get_all(
			"Smart Project",
			filters={
				"project_manager": manager_email,
				"status": ["in", ["Planning", "Active", "On Hold"]]
			},
			fields=["name", "title", "status", "start_date", "end_date"]
		)

		if not projects:
			continue

		# Build project summary
		project_rows = ""
		overdue_count = 0

		for project in projects:
			# Get task stats for this project
			task_stats = frappe.db.sql("""
				SELECT
					COUNT(*) as total,
					SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
					SUM(CASE WHEN status IN ('Open', 'Working', 'Pending Review') AND due_date < %s THEN 1 ELSE 0 END) as overdue
				FROM `tabSmart Task`
				WHERE project = %s
			""", (today(), project.name), as_dict=True)[0]

			total_tasks = task_stats.total or 0
			completed_tasks = task_stats.completed or 0
			overdue_tasks = task_stats.overdue or 0

			if overdue_tasks > 0:
				overdue_count += 1

			# Calculate project progress
			progress = 0
			if total_tasks > 0:
				progress = round((completed_tasks / total_tasks) * 100)

			# Check if project is overdue
			project_overdue = ""
			if project.end_date and getdate(project.end_date) < today_date:
				project_overdue = ' style="color: #dc3545;"'

			end_date_display = formatdate(project.end_date) if project.end_date else "Not set"

			project_rows += f"""
			<tr>
				<td style="padding: 10px; border: 1px solid #ddd;">
					<a href="{frappe.utils.get_url()}/app/smart-project/{project.name}">{project.title}</a>
				</td>
				<td style="padding: 10px; border: 1px solid #ddd;">{project.status}</td>
				<td style="padding: 10px; border: 1px solid #ddd;"{project_overdue}>{end_date_display}</td>
				<td style="padding: 10px; border: 1px solid #ddd;">{progress}%</td>
				<td style="padding: 10px; border: 1px solid #ddd;">{completed_tasks}/{total_tasks}</td>
				<td style="padding: 10px; border: 1px solid #ddd; color: {'#dc3545' if overdue_tasks > 0 else '#28a745'};">
					{overdue_tasks}
				</td>
			</tr>
			"""

		# Get manager name
		manager_name = frappe.db.get_value("User", manager_email, "full_name") or manager_email

		try:
			subject = f"Smart Pro Weekly Project Report - {formatdate(today())}"
			message = f"""
			<h2>Weekly Project Report</h2>
			<p>Hello {manager_name},</p>
			<p>Here is your weekly project status summary:</p>

			<h3>Summary</h3>
			<ul>
				<li><strong>Total Projects:</strong> {len(projects)}</li>
				<li><strong>Projects with Overdue Tasks:</strong> {overdue_count}</li>
			</ul>

			<h3>Project Details</h3>
			<table style="border-collapse: collapse; width: 100%;">
				<thead>
					<tr style="background-color: #f8f9fa;">
						<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Project</th>
						<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Status</th>
						<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">End Date</th>
						<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Progress</th>
						<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Tasks</th>
						<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Overdue</th>
					</tr>
				</thead>
				<tbody>
					{project_rows}
				</tbody>
			</table>

			<p style="margin-top: 20px;">
				<a href="{frappe.utils.get_url()}/smart-pro/home"
				   style="background-color: #5e64ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
					Open Smart Pro
				</a>
			</p>

			<p style="color: #666; font-size: 12px; margin-top: 20px;">
				This is an automated weekly report from Smart Pro.
			</p>
			"""

			frappe.sendmail(
				recipients=[manager_email],
				subject=subject,
				message=message,
				now=True
			)

			frappe.logger().info(f"Smart Pro: Sent weekly report to {manager_email}")

		except Exception as e:
			frappe.logger().error(f"Smart Pro: Error sending weekly report to {manager_email}: {str(e)}")


def daily():
	"""Daily scheduled task - runs project and task reminders"""
	send_project_end_date_reminders()
	send_task_due_date_reminders()


def weekly():
	"""Weekly scheduled task - runs weekly report"""
	send_weekly_project_report()
