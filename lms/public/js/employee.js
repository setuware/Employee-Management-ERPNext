frappe.pages['employee-list'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Employee Management',
		single_column: true
	});
}
