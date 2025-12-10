"""
Push Notifications and Email Notifications for Smart Pro PWA
Handles sending push notifications and beautiful email notifications
"""

import frappe
import json
from frappe.utils import now_datetime, get_url


def is_email_notifications_enabled():
    """Check if email notifications are enabled in settings"""
    try:
        return frappe.db.get_single_value("Smart Pro Settings", "enable_email_notifications") or False
    except Exception:
        return False


def is_push_notifications_enabled():
    """Check if push notifications are enabled in settings"""
    try:
        return frappe.db.get_single_value("Smart Pro Settings", "enable_notifications") or True
    except Exception:
        return True


def get_app_name():
    """Get app name from settings"""
    try:
        return frappe.db.get_single_value("Smart Pro Settings", "app_name") or "Smart Pro"
    except Exception:
        return "Smart Pro"


class EmailTemplates:
    """Beautiful HTML email templates for Smart Pro"""

    @staticmethod
    def get_base_template(title, content, action_url=None, action_text=None):
        """Base email template with modern design"""
        app_name = get_app_name()
        site_url = get_url()

        action_button = ""
        if action_url and action_text:
            action_button = f'''
            <tr>
              <td style="padding: 30px 0;">
                <a href="{action_url}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px; box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);">
                  {action_text}
                </a>
              </td>
            </tr>
            '''

        return f'''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%;">
          <!-- Header -->
          <tr>
            <td style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding: 32px 40px; border-radius: 16px 16px 0 0;">
              <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 700;">{app_name}</h1>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td style="background: white; padding: 40px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <h2 style="margin: 0 0 20px 0; color: #1e293b; font-size: 20px; font-weight: 600;">{title}</h2>
                    {content}
                  </td>
                </tr>
                {action_button}
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 24px 40px; text-align: center;">
              <p style="margin: 0; color: #64748b; font-size: 13px;">
                This email was sent by {app_name}.<br>
                <a href="{site_url}" style="color: #3b82f6; text-decoration: none;">{site_url}</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
'''

    @staticmethod
    def task_assignment(task_doc):
        """Email template for task assignment"""
        site_url = get_url()
        project_title = frappe.db.get_value("Smart Project", task_doc.project, "title") if task_doc.project else "N/A"

        content = f'''
        <div style="background: #f8fafc; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Task</span><br>
                <span style="color: #1e293b; font-size: 16px; font-weight: 600;">{task_doc.title}</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Project</span><br>
                <span style="color: #1e293b; font-size: 15px;">{project_title}</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Priority</span><br>
                <span style="display: inline-block; padding: 4px 12px; background: {"#fee2e2" if task_doc.priority == "Critical" else "#fef3c7" if task_doc.priority == "High" else "#dbeafe"}; color: {"#dc2626" if task_doc.priority == "Critical" else "#d97706" if task_doc.priority == "High" else "#2563eb"}; border-radius: 20px; font-size: 13px; font-weight: 500;">
                  {task_doc.priority or "Medium"}
                </span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Due Date</span><br>
                <span style="color: #1e293b; font-size: 15px;">{task_doc.due_date or "Not set"}</span>
              </td>
            </tr>
          </table>
        </div>
        <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0;">
          You have been assigned a new task. Please review the details and start working on it.
        </p>
        '''

        return EmailTemplates.get_base_template(
            "New Task Assigned",
            content,
            f"{site_url}/smart-pro/task/{task_doc.name}",
            "View Task"
        )

    @staticmethod
    def task_update(task_doc):
        """Email template for task updates"""
        site_url = get_url()

        status_colors = {
            "Open": ("#dbeafe", "#2563eb"),
            "Working": ("#fef3c7", "#d97706"),
            "Completed": ("#d1fae5", "#059669"),
            "Cancelled": ("#fee2e2", "#dc2626"),
        }
        bg_color, text_color = status_colors.get(task_doc.status, ("#f1f5f9", "#64748b"))

        content = f'''
        <div style="background: #f8fafc; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Task</span><br>
                <span style="color: #1e293b; font-size: 16px; font-weight: 600;">{task_doc.title}</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Status</span><br>
                <span style="display: inline-block; padding: 4px 12px; background: {bg_color}; color: {text_color}; border-radius: 20px; font-size: 13px; font-weight: 500;">
                  {task_doc.status}
                </span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Progress</span><br>
                <div style="background: #e2e8f0; border-radius: 10px; height: 10px; width: 100%; margin-top: 8px;">
                  <div style="background: linear-gradient(90deg, #3b82f6, #2563eb); border-radius: 10px; height: 10px; width: {task_doc.progress or 0}%;"></div>
                </div>
                <span style="color: #1e293b; font-size: 14px; font-weight: 600;">{task_doc.progress or 0}%</span>
              </td>
            </tr>
          </table>
        </div>
        '''

        return EmailTemplates.get_base_template(
            "Task Updated",
            content,
            f"{site_url}/smart-pro/task/{task_doc.name}",
            "View Task"
        )

    @staticmethod
    def date_request_pending(request_doc):
        """Email template for pending date request (to approver)"""
        site_url = get_url()

        content = f'''
        <div style="background: #f8fafc; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Employee</span><br>
                <span style="color: #1e293b; font-size: 16px; font-weight: 600;">{request_doc.employee_name}</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Request Type</span><br>
                <span style="display: inline-block; padding: 4px 12px; background: #dbeafe; color: #2563eb; border-radius: 20px; font-size: 13px; font-weight: 500;">
                  {request_doc.request_type}
                </span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Dates</span><br>
                <span style="color: #1e293b; font-size: 15px;">{request_doc.from_date} to {request_doc.to_date}</span>
                <span style="color: #64748b; font-size: 13px;"> ({request_doc.total_days or 1} days)</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Reason</span><br>
                <span style="color: #475569; font-size: 14px; line-height: 1.5;">{request_doc.reason or "No reason provided"}</span>
              </td>
            </tr>
          </table>
        </div>
        <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0;">
          Please review and take action on this request.
        </p>
        '''

        return EmailTemplates.get_base_template(
            "Date Request Pending Approval",
            content,
            f"{site_url}/smart-pro/approvals",
            "Review Request"
        )

    @staticmethod
    def date_request_approved(request_doc):
        """Email template for approved date request (to employee)"""
        site_url = get_url()

        content = f'''
        <div style="text-align: center; margin-bottom: 24px;">
          <div style="display: inline-block; width: 64px; height: 64px; background: #d1fae5; border-radius: 50%; line-height: 64px;">
            <span style="font-size: 32px;">✓</span>
          </div>
        </div>
        <div style="background: #f8fafc; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Request Type</span><br>
                <span style="color: #1e293b; font-size: 16px; font-weight: 600;">{request_doc.request_type}</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Dates</span><br>
                <span style="color: #1e293b; font-size: 15px;">{request_doc.from_date} to {request_doc.to_date}</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Status</span><br>
                <span style="display: inline-block; padding: 4px 12px; background: #d1fae5; color: #059669; border-radius: 20px; font-size: 13px; font-weight: 500;">
                  Approved
                </span>
              </td>
            </tr>
          </table>
        </div>
        <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0;">
          Your request has been approved. You're all set!
        </p>
        '''

        return EmailTemplates.get_base_template(
            "Date Request Approved",
            content,
            f"{site_url}/smart-pro/date-requests",
            "View Details"
        )

    @staticmethod
    def date_request_rejected(request_doc):
        """Email template for rejected date request (to employee)"""
        site_url = get_url()

        content = f'''
        <div style="text-align: center; margin-bottom: 24px;">
          <div style="display: inline-block; width: 64px; height: 64px; background: #fee2e2; border-radius: 50%; line-height: 64px;">
            <span style="font-size: 32px;">✕</span>
          </div>
        </div>
        <div style="background: #f8fafc; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Request Type</span><br>
                <span style="color: #1e293b; font-size: 16px; font-weight: 600;">{request_doc.request_type}</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Dates</span><br>
                <span style="color: #1e293b; font-size: 15px;">{request_doc.from_date} to {request_doc.to_date}</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0;">
                <span style="color: #64748b; font-size: 13px;">Status</span><br>
                <span style="display: inline-block; padding: 4px 12px; background: #fee2e2; color: #dc2626; border-radius: 20px; font-size: 13px; font-weight: 500;">
                  Rejected
                </span>
              </td>
            </tr>
            {"<tr><td style='padding: 8px 0;'><span style='color: #64748b; font-size: 13px;'>Comments</span><br><span style='color: #475569; font-size: 14px;'>" + (request_doc.comments or "No comments provided") + "</span></td></tr>" if request_doc.comments else ""}
          </table>
        </div>
        <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0;">
          Unfortunately, your request was not approved. Please contact your manager for more details.
        </p>
        '''

        return EmailTemplates.get_base_template(
            "Date Request Rejected",
            content,
            f"{site_url}/smart-pro/date-requests",
            "View Details"
        )


class PushNotificationManager:
    """Manages push notifications for PWA"""

    @staticmethod
    def send_task_assignment_notification(task_doc):
        """Send notification when a task is assigned"""
        try:
            if task_doc.assigned_to:
                title = f"New Task: {task_doc.title}"
                body = f"You have been assigned a new task in project {task_doc.project}"

                # Send push notification
                if is_push_notifications_enabled():
                    PushNotificationManager._send_notification(
                        task_doc.assigned_to,
                        title,
                        body,
                        {
                            "type": "task_assignment",
                            "doctype": "Smart Task",
                            "name": task_doc.name,
                            "url": f"/app/smart-task/{task_doc.name}"
                        }
                    )

                # Send email notification
                if is_email_notifications_enabled():
                    PushNotificationManager._send_email(
                        task_doc.assigned_to,
                        f"New Task Assigned: {task_doc.title}",
                        EmailTemplates.task_assignment(task_doc)
                    )
        except Exception as e:
            frappe.log_error(str(e), "Push Notification - Task Assignment")

    @staticmethod
    def send_task_update_notification(task_doc):
        """Send notification when a task is updated"""
        try:
            if task_doc.assigned_to:
                title = f"Task Updated: {task_doc.title}"
                body = f"Status: {task_doc.status} | Progress: {task_doc.progress}%"

                # Send push notification
                if is_push_notifications_enabled():
                    PushNotificationManager._send_notification(
                        task_doc.assigned_to,
                        title,
                        body,
                        {
                            "type": "task_update",
                            "doctype": "Smart Task",
                            "name": task_doc.name,
                            "url": f"/app/smart-task/{task_doc.name}"
                        }
                    )

                # Send email only for significant updates (status change to completed)
                if is_email_notifications_enabled() and task_doc.status == "Completed":
                    PushNotificationManager._send_email(
                        task_doc.assigned_to,
                        f"Task Completed: {task_doc.title}",
                        EmailTemplates.task_update(task_doc)
                    )
        except Exception as e:
            frappe.log_error(str(e), "Push Notification - Task Update")

    @staticmethod
    def send_date_request_notification(request_doc):
        """Send notification for date requests"""
        try:
            if request_doc.approver:
                title = f"Date Request from {request_doc.employee_name}"
                body = f"{request_doc.request_type}: {request_doc.from_date} to {request_doc.to_date}"

                # Send push notification
                if is_push_notifications_enabled():
                    PushNotificationManager._send_notification(
                        request_doc.approver,
                        title,
                        body,
                        {
                            "type": "date_request",
                            "doctype": "Employee Date Request",
                            "name": request_doc.name,
                            "url": f"/app/employee-date-request/{request_doc.name}"
                        }
                    )

                # Send email notification to approver
                if is_email_notifications_enabled():
                    PushNotificationManager._send_email(
                        request_doc.approver,
                        f"Date Request from {request_doc.employee_name}",
                        EmailTemplates.date_request_pending(request_doc)
                    )
        except Exception as e:
            frappe.log_error(str(e), "Push Notification - Date Request")

    @staticmethod
    def send_date_request_status_notification(request_doc, status):
        """Send notification when date request status changes"""
        try:
            # Get employee's user_id
            employee_user = None
            if request_doc.employee:
                employee_user = frappe.db.get_value("Employee", request_doc.employee, "user_id")

            if employee_user:
                title = f"Date Request {status}"
                body = f"Your {request_doc.request_type} request has been {status.lower()}"

                # Send push notification
                if is_push_notifications_enabled():
                    PushNotificationManager._send_notification(
                        employee_user,
                        title,
                        body,
                        {
                            "type": f"date_request_{status.lower()}",
                            "doctype": "Employee Date Request",
                            "name": request_doc.name,
                            "url": f"/app/employee-date-request/{request_doc.name}"
                        }
                    )

                # Send email notification
                if is_email_notifications_enabled():
                    if status == "Approved":
                        email_content = EmailTemplates.date_request_approved(request_doc)
                    else:
                        email_content = EmailTemplates.date_request_rejected(request_doc)

                    PushNotificationManager._send_email(
                        employee_user,
                        f"Date Request {status}",
                        email_content
                    )
        except Exception as e:
            frappe.log_error(str(e), f"Push Notification - Date Request {status}")

    @staticmethod
    def send_project_update_notification(project_doc, project_manager):
        """Send notification for project updates"""
        try:
            title = f"Project Update: {project_doc.title}"
            body = f"Status changed to {project_doc.status}"

            if is_push_notifications_enabled():
                PushNotificationManager._send_notification(
                    project_manager,
                    title,
                    body,
                    {
                        "type": "project_update",
                        "doctype": "Smart Project",
                        "name": project_doc.name,
                        "url": f"/app/smart-project/{project_doc.name}"
                    }
                )
        except Exception as e:
            frappe.log_error(str(e), "Push Notification - Project Update")

    @staticmethod
    def _send_notification(user, title, body, data):
        """Send push notification to user"""
        try:
            # Store notification in database for later retrieval
            notification = frappe.get_doc({
                "doctype": "Smart Pro Notification",
                "user": user,
                "title": title,
                "body": body,
                "data": json.dumps(data),
                "status": "pending",
                "created_at": now_datetime()
            })
            notification.insert(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(str(e), "Push Notification - Send")

    @staticmethod
    def _send_email(user, subject, html_content):
        """Send beautiful HTML email to user"""
        try:
            frappe.sendmail(
                recipients=[user],
                subject=subject,
                message=html_content,
                delayed=False
            )
        except Exception as e:
            frappe.log_error(str(e), "Email Notification - Send")

@frappe.whitelist()
def subscribe_to_notifications():
    """Subscribe user to push notifications"""
    try:
        user = frappe.session.user
        
        # Store subscription info
        subscription = frappe.get_doc({
            "doctype": "Smart Pro Subscription",
            "user": user,
            "subscribed": True,
            "subscribed_at": now_datetime()
        })
        subscription.insert(ignore_permissions=True)
        
        return {"status": "success", "message": "Subscribed to notifications"}
    except Exception as e:
        frappe.log_error(str(e), "Push Notification - Subscribe")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_pending_notifications():
    """Get pending notifications for current user"""
    try:
        user = frappe.session.user
        
        notifications = frappe.get_list(
            "Smart Pro Notification",
            filters={
                "user": user,
                "status": "pending"
            },
            fields=["name", "title", "body", "data", "created_at"],
            order_by="created_at desc",
            limit_page_length=50
        )
        
        return {"status": "success", "notifications": notifications}
    except Exception as e:
        frappe.log_error(str(e), "Push Notification - Get Pending")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def mark_notification_as_read(notification_name):
    """Mark notification as read"""
    try:
        notification = frappe.get_doc("Smart Pro Notification", notification_name)
        notification.status = "read"
        notification.save(ignore_permissions=True)
        
        return {"status": "success", "message": "Notification marked as read"}
    except Exception as e:
        frappe.log_error(str(e), "Push Notification - Mark Read")
        return {"status": "error", "message": str(e)}