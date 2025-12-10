// Copyright (c) 2025, sammish and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Project Assignment", {
	refresh(frm) {
		// Add "Generate Scope" button for AI-powered scope generation
		frm.add_custom_button(__('Generate Scope'), function() {
			if (!frm.doc.project) {
				frappe.msgprint(__('Please select a Project first'));
				return;
			}

			// Get project title
			frappe.db.get_value('Smart Project', frm.doc.project, 'title', function(r) {
				if (!r || !r.title) {
					frappe.msgprint(__('Could not fetch project title'));
					return;
				}

				frappe.show_alert({
					message: __('Generating project scope...'),
					indicator: 'blue'
				});

				// Role name is the same as role field value (Smart Role uses name as the role)
				generate_scope(frm, r.title, frm.doc.employee_name, frm.doc.role);
			});
		}, __('AI'));
	}
});

function generate_scope(frm, project_title, employee_name, role) {
	frappe.call({
		method: 'smart_pro.smart_pro.api.projects.generate_project_scope',
		args: {
			project_title: project_title,
			employee_name: employee_name || '',
			role: role || ''
		},
		callback: function(r) {
			if (r.message) {
				if (r.message.success) {
					frm.set_value('project_scope', r.message.description);
					frappe.show_alert({
						message: __('Project scope generated successfully!'),
						indicator: 'green'
					});
				} else {
					frappe.msgprint({
						title: __('Error'),
						message: r.message.message,
						indicator: 'red'
					});
				}
			}
		}
	});
}
