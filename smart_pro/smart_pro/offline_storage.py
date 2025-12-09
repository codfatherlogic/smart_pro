"""
Offline Storage Management for Smart Pro PWA
Handles caching and synchronization of data when offline
"""

import frappe
import json
from frappe.utils import now_datetime

class OfflineStorageManager:
    """Manages offline data storage and synchronization"""
    
    @staticmethod
    def cache_project_data(user):
        """Cache project data for offline access"""
        try:
            projects = frappe.get_list(
                "Smart Project",
                filters={"project_manager": user},
                fields=["name", "title", "status", "start_date", "end_date", "budget_amount"],
                limit_page_length=100
            )
            
            # Store in session storage (will be cleared when browser closes)
            frappe.session.data["cached_projects"] = {
                "timestamp": now_datetime().isoformat(),
                "data": projects
            }
            
            return {"status": "success", "count": len(projects)}
        except Exception as e:
            frappe.log_error(str(e), "Offline Storage - Cache Projects")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def cache_task_data(user):
        """Cache task data for offline access"""
        try:
            tasks = frappe.get_list(
                "Smart Task",
                filters={"assigned_to": user},
                fields=["name", "title", "project", "status", "priority", "due_date", "progress"],
                limit_page_length=100
            )
            
            frappe.session.data["cached_tasks"] = {
                "timestamp": now_datetime().isoformat(),
                "data": tasks
            }
            
            return {"status": "success", "count": len(tasks)}
        except Exception as e:
            frappe.log_error(str(e), "Offline Storage - Cache Tasks")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def cache_date_request_data(user):
        """Cache date request data for offline access"""
        try:
            requests = frappe.get_list(
                "Employee Date Request",
                filters={"approver": user, "status": "Pending Approval"},
                fields=["name", "employee", "employee_name", "request_type", "from_date", "to_date", "reason"],
                limit_page_length=100
            )
            
            frappe.session.data["cached_requests"] = {
                "timestamp": now_datetime().isoformat(),
                "data": requests
            }
            
            return {"status": "success", "count": len(requests)}
        except Exception as e:
            frappe.log_error(str(e), "Offline Storage - Cache Requests")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def sync_offline_changes(user, changes):
        """Synchronize offline changes when back online"""
        try:
            synced_count = 0
            errors = []

            # Prepare a dictionary to batch fetch documents
            docs_to_update = {}
            docs_to_create = []

            for change in changes:
                doctype = change.get("doctype")
                docname = change.get("name")
                action = change.get("action")
                data = change.get("data", {})

                if action == "update":
                    docs_to_update.setdefault(doctype, []).append((docname, data))
                elif action == "create":
                    docs_to_create.append((doctype, data))

            # Fetch all documents that need to be updated
            for doctype, docnames in docs_to_update.items():
                try:
                    # Create a mapping of docname to data for O(1) lookups
                    docname_to_data = {docname: data for docname, data in docnames}
                    docname_list = list(docname_to_data.keys())
                    
                    fetched_docs = frappe.get_all(doctype, filters={"name": ["in", docname_list]}, as_dict=True)
                    
                    # Track which documents were found
                    found_names = set()
                    
                    for doc in fetched_docs:
                        if doc.name in docname_to_data:
                            found_names.add(doc.name)
                            try:
                                doc.update(docname_to_data[doc.name])
                                doc.save()
                                synced_count += 1
                            except Exception as e:
                                errors.append({
                                    "doctype": doctype,
                                    "name": doc.name,
                                    "error": str(e)
                                })
                    
                    # Log missing documents
                    missing_names = set(docname_list) - found_names
                    for missing_name in missing_names:
                        errors.append({
                            "doctype": doctype,
                            "name": missing_name,
                            "error": "Document not found"
                        })
                except Exception as e:
                    errors.append({
                        "doctype": doctype,
                        "name": "batch_fetch",
                        "error": str(e)
                    })

            # Create new documents in batch
            for doctype, data in docs_to_create:
                try:
                    doc = frappe.get_doc({
                        "doctype": doctype,
                        **data
                    })
                    doc.insert()
                    synced_count += 1
                except Exception as e:
                    errors.append({
                        "doctype": doctype,
                        "name": data.get("name", "new"),
                        "error": str(e)
                    })

            return {
                "status": "success",
                "synced": synced_count,
                "errors": errors
            }

        
        except Exception as e:
            frappe.log_error(str(e), "Offline Storage - Sync Changes")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def get_cache_status(user):
        """Get the status of cached data"""
        status = {
            "projects": None,
            "tasks": None,
            "requests": None
        }
        
        if "cached_projects" in frappe.session.data:
            status["projects"] = frappe.session.data["cached_projects"]["timestamp"]
        
        if "cached_tasks" in frappe.session.data:
            status["tasks"] = frappe.session.data["cached_tasks"]["timestamp"]
        
        if "cached_requests" in frappe.session.data:
            status["requests"] = frappe.session.data["cached_requests"]["timestamp"]
        
        return status

@frappe.whitelist()
def cache_offline_data():
    """Whitelisted method to cache data for offline access"""
    user = frappe.session.user
    manager = OfflineStorageManager()
    
    results = {
        "projects": manager.cache_project_data(user),
        "tasks": manager.cache_task_data(user),
        "requests": manager.cache_date_request_data(user)
    }
    
    return results

@frappe.whitelist()
def sync_offline_changes(changes):
    """Whitelisted method to sync offline changes"""
    user = frappe.session.user
    manager = OfflineStorageManager()
    
    # Parse JSON string if needed
    if isinstance(changes, str):
        try:
            changes = json.loads(changes)
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"Invalid JSON: {str(e)}"}
    
    return manager.sync_offline_changes(user, changes)

@frappe.whitelist()
def get_offline_cache_status():
    """Whitelisted method to get cache status"""
    user = frappe.session.user
    manager = OfflineStorageManager()
    
    return manager.get_cache_status(user)