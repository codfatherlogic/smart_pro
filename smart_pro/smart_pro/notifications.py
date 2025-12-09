"""
Push Notifications for Smart Pro PWA
Handles sending push notifications for task updates and approvals
"""

import frappe
import json
from frappe.utils import now_datetime

class PushNotificationManager:
    """Manages push notifications for PWA"""
    
    @staticmethod
    def send_task_assignment_notification(task_doc):
        """Send notification when a task is assigned"""
        try:
            if task_doc.assigned_to:
                title = f"New Task: {task_doc.title}"
                body = f"You have been assigned a new task in project {task_doc.project}"
                
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
        except Exception as e:
            frappe.log_error(str(e), "Push Notification - Task Assignment")
    
    @staticmethod
    def send_task_update_notification(task_doc):
        """Send notification when a task is updated"""
        try:
            if task_doc.assigned_to:
                title = f"Task Updated: {task_doc.title}"
                body = f"Status: {task_doc.status} | Progress: {task_doc.progress}%"
                
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
        except Exception as e:
            frappe.log_error(str(e), "Push Notification - Task Update")
    
    @staticmethod
    def send_date_request_notification(request_doc):
        """Send notification for date requests"""
        try:
            if request_doc.approver:
                title = f"Date Request from {request_doc.employee_name}"
                body = f"{request_doc.request_type}: {request_doc.from_date} to {request_doc.to_date}"
                
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
        except Exception as e:
            frappe.log_error(str(e), "Push Notification - Date Request")
    
    @staticmethod
    def send_project_update_notification(project_doc, project_manager):
        """Send notification for project updates"""
        try:
            title = f"Project Update: {project_doc.title}"
            body = f"Status changed to {project_doc.status}"
            
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
            
            # In a production environment, you would integrate with a service like:
            # - Firebase Cloud Messaging (FCM)
            # - OneSignal
            # - AWS SNS
            # For now, we just store the notification
            
        except Exception as e:
            frappe.log_error(str(e), "Push Notification - Send")

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