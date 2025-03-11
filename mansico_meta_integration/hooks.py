app_name = "mansico_meta_integration"
app_title = "Mansico Meta Integration"
app_publisher = "Mansy"
app_description = "This project is about syncing Facebook leads with ERPnext, When Clients fill Facebook ads instant forms app automatic fetch new created leads and create lead automatic in Lead doctype. Also on changing the Lead Status the new status sent to meta Pixel."
app_email = "ahmedmansy265@gmail.com"
app_license = "mit"
required_apps = ["erpnext"]

doc_events = {
    "Lead": {
        # will run before a ToDo record is inserted into database
        "validate": "mansico_meta_integration.overrides.validate_lead",
    }
}

import frappe
if frappe.db.exists("DocType", "CRM Lead"):
    doc_events["CRM Lead"] = {
        "validate": "mansico_meta_integration.overrides.validate_crmlead",
    }
# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [
		"mansico_meta_integration.tasks.all"
	],
	"daily": [
		"mansico_meta_integration.tasks.daily"
	],
	"hourly": [
		"mansico_meta_integration.tasks.hourly"
	],
	"weekly": [
		"mansico_meta_integration.tasks.weekly"
	],
	"monthly": [
		"mansico_meta_integration.tasks.monthly"
	],
}
