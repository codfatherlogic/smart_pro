# Smart Pro PWA Entry Point
# This file allows the /smart-pro route to serve the PWA

import frappe

no_cache = 1

def get_context(context):
    """Set up context for the PWA"""
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    context.csrf_token = csrf_token
    return context
