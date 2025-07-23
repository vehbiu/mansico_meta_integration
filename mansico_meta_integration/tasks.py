

import frappe
from mansico_meta_integration.mansico_meta_integration.doctype.sync_new_add.sync_new_add import FetchLeads


def _process_sync_records_by_frequency(frequency):
    """Process sync records for a given frequency."""
    sync_new_add = frappe.db.get_all("Sync New Add", {"event_frequency": frequency, "docstatus": 1}, pluck="name")
    for name in sync_new_add:
        fetch = FetchLeads(name)
        fetch.fetch_leads()

@frappe.whitelist()
def all():
    _process_sync_records_by_frequency("All")

@frappe.whitelist()
def daily():
    _process_sync_records_by_frequency("Daily")

@frappe.whitelist()
def hourly():
    _process_sync_records_by_frequency("Hourly")

@frappe.whitelist()
def weekly():
    _process_sync_records_by_frequency("Weekly")

@frappe.whitelist()
def monthly():
    _process_sync_records_by_frequency("Monthly")

@frappe.whitelist()
def every_30_minutes():
    _process_sync_records_by_frequency("Every 30 Minutes")

@frappe.whitelist()
def every_15_minutes():
    _process_sync_records_by_frequency("Every 15 Minutes")

@frappe.whitelist()
def every_10_minutes():
    _process_sync_records_by_frequency("Every 10 Minutes")

@frappe.whitelist()
def every_5_minutes():
    _process_sync_records_by_frequency("Every 5 Minutes")