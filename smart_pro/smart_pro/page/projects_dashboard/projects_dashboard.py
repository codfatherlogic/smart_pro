import frappe


def get_context(context):
	"""Get context for projects dashboard page"""
	context.title = "Projects Dashboard"
	context.no_cache = 1
	
	# Check user permissions
	if not frappe.has_permission("Smart Project", "read"):
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
	
	# Add any additional context needed
	context.breadcrumbs = [
		{"label": "Home", "route": "/app"},
		{"label": "Smart Pro", "route": "/app/smart-pro"},
		{"label": "Projects Dashboard", "route": "/app/projects_dashboard"}
	]
	
	return context