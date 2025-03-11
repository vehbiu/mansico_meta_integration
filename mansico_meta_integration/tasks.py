

import frappe
from mansico_meta_integration.mansico_meta_integration.doctype.sync_new_add.sync_new_add import FetchLeads


@frappe.whitelist()
def all():
    sync_new_add = frappe.db.get_all("Sync New Add", {"event_frequency": "All", "docstatus": 1}, pluck="name")
    for name in sync_new_add:
        fetch = FetchLeads(name)
        fetch.fetch_leads()

@frappe.whitelist()
def daily():
    sync_new_add = frappe.db.get_all("Sync New Add", {"event_frequency": "Daily", "docstatus": 1}, pluck="name")
    for name in sync_new_add:
        fetch = FetchLeads(name)
        fetch.fetch_leads()

@frappe.whitelist()
def hourly():
    sync_new_add = frappe.db.get_all("Sync New Add", {"event_frequency": "Hourly", "docstatus": 1}, pluck="name")
    for name in sync_new_add:
        fetch = FetchLeads(name)
        fetch.fetch_leads()

@frappe.whitelist()
def weekly():
    sync_new_add = frappe.db.get_all("Sync New Add", {"event_frequency": "Weekly", "docstatus": 1}, pluck="name")
    for name in sync_new_add:
        fetch = FetchLeads(name)
        fetch.fetch_leads()

@frappe.whitelist()
def monthly():
    sync_new_add = frappe.db.get_all("Sync New Add", {"event_frequency": "Monthly", "docstatus": 1}, pluck="name")
    for name in sync_new_add:
        fetch = FetchLeads(name)
        fetch.fetch_leads()