// Copyright (c) 2025, sammish and contributors
// For license information, please see license.txt

frappe.ui.form.on("Smart Project", {
	refresh(frm) {
		// Add "Generate Description" button if AI features are enabled
		frm.add_custom_button(__('Generate Description'), function() {
			if (!frm.doc.title) {
				frappe.msgprint(__('Please enter a Project Title first'));
				return;
			}

			frappe.show_alert({
				message: __('Generating description...'),
				indicator: 'blue'
			});

			frappe.call({
				method: 'smart_pro.smart_pro.api.projects.generate_project_description',
				args: {
					title: frm.doc.title
				},
				callback: function(r) {
					if (r.message) {
						if (r.message.success) {
							frm.set_value('description', r.message.description);
							frappe.show_alert({
								message: __('Description generated successfully!'),
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
		}, __('AI'));
	},

	title() {
		// Optional: Auto-trigger description generation when title changes
		// Uncomment if you want auto-generation on title change
		// this.frm.trigger('generate_description_on_title');
	}
});
