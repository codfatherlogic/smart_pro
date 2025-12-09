# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SmartProSettings(Document):
	pass


def get_settings():
	"""Get Smart Pro Settings singleton"""
	try:
		return frappe.get_single("Smart Pro Settings")
	except Exception:
		# Return a dummy object if settings don't exist yet
		return frappe._dict({
			"users_with_full_access": [],
			"roles_with_full_access": "System Manager"
		})


def user_has_full_access(user=None):
	"""Check if user has full access to view all projects and tasks"""
	if not user:
		user = frappe.session.user

	# Administrator always has full access
	if user == "Administrator":
		return True

	# System Manager always has full access
	user_roles = frappe.get_roles(user)
	if "System Manager" in user_roles:
		return True

	settings = get_settings()

	# Check if user is in the users_with_full_access table
	for row in settings.users_with_full_access:
		if row.user == user and row.can_view_all_projects:
			return True

	# Check if user has any of the roles with full access
	if settings.roles_with_full_access:
		roles_with_access = [r.strip() for r in settings.roles_with_full_access.split("\n") if r.strip()]

		for role in roles_with_access:
			if role in user_roles:
				return True

	return False


def user_can_view_all_tasks(user=None):
	"""Check if user can view all tasks"""
	if not user:
		user = frappe.session.user

	# Administrator always has full access
	if user == "Administrator":
		return True

	# System Manager always has full access
	user_roles = frappe.get_roles(user)
	if "System Manager" in user_roles:
		return True

	settings = get_settings()

	# Check if user is in the users_with_full_access table with task permission
	for row in settings.users_with_full_access:
		if row.user == user and row.can_view_all_tasks:
			return True

	# Check if user has any of the roles with full access
	if settings.roles_with_full_access:
		roles_with_access = [r.strip() for r in settings.roles_with_full_access.split("\n") if r.strip()]

		for role in roles_with_access:
			if role in user_roles:
				return True

	return False
