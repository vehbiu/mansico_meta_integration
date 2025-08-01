# Copyright (c) 2023, mansy and contributors
# For license information, please see license.txt

import datetime
import json
import time
import traceback

import requests
import frappe
from frappe.model.document import Document

from mansico_meta_integration.mansico_meta_integration.doctype.sync_new_add.meta_integraion_objects import UserData, CustomData, Payload


@frappe.whitelist()
def get_credentials():
    return frappe.get_doc("Meta Facebook Settings")

class Request:
    """Handle Facebook Graph API request construction."""
    
    def __init__(self, url, version, page_id, f_payload=None, params=None):
        self.url = url
        self.version = f'v{version}'
        self.page_id = page_id
        self.f_payload = f_payload
        self.params = params
    
    @property
    def get_url(self):
        return f"{self.url}/{self.version}/{self.page_id}"

def _handle_api_error(response, request, title="Error"):
    """Centralized error handling for API responses."""
    try:
        error_data = frappe._dict(response.json()).get("error")
        if error_data:
            error_message = f"url : {request.get_url}<br>params : {request.params}<br><br>"
            error_message += "<br>".join([f"{key} : {value}" for key, value in error_data.items()])
            frappe.throw(error_message, title=title)
    except (ValueError, KeyError):
        # Handle cases where response is not valid JSON
        frappe.throw(f"API Error: {response.text}", title=title)

class RequestPageAccessToken:
    """Handle page access token requests."""
    
    def __init__(self, request):
        self.request = request
        self.page_access_token = None

    def get_page_access_token(self):
        """Get page access token from Facebook API."""
        try:
            response = requests.get(
                self.request.get_url, 
                params=self.request.params, 
                json=self.request.params,
                timeout=30
            )
            _handle_api_error(response, self.request)
            self.page_access_token = frappe._dict(response.json()).get("access_token")
            return self.page_access_token
        except requests.exceptions.Timeout:
            frappe.throw(f"Request timed out while getting page access token for URL: {self.request.get_url}", title="Timeout Error")
        except requests.exceptions.RequestException as e:
            frappe.throw(f"Network error while getting page access token: {str(e)}", title="Network Error")

class RequestLeadGenForms:
    """Handle lead generation form requests."""
    
    def __init__(self, request):
        self.request = request
        self.lead_forms = None

    def get_lead_forms(self):
        """Get lead forms from Facebook API."""
        try:
            response = requests.get(
                self.request.get_url, 
                params=self.request.params, 
                json=self.request.params,
                timeout=30
            )
            _handle_api_error(response, self.request)
            self.lead_forms = frappe._dict(response.json())
            return self.lead_forms
        except requests.exceptions.Timeout:
            frappe.throw(f"Request timed out while getting lead forms for URL: {self.request.get_url}", title="Timeout Error")
        except requests.exceptions.RequestException as e:
            frappe.throw(f"Network error while getting lead forms: {str(e)}", title="Network Error")

class AppendForms:
    """Handle appending forms to document."""
    
    def __init__(self, lead_forms, doc):
        self.lead_forms = lead_forms
        self.doc = doc

    def append_forms(self):
        if self.doc.force_fetch:
            self.doc.set("table_hsya", [])

            for lead_form in self.lead_forms.get("data", []):
                self.doc.append("table_hsya", {
                    "form_id": lead_form.get("id"),
                    "form_name": lead_form.get("name"),
                    "created_time": lead_form.get("created_time"),
                    "leads_count": lead_form.get("leads_count"),
                    "page": lead_form.get("page"),
                    "questions": frappe._dict({"questions": lead_form.get("questions")}),
                })

        if self.doc.fetch_map_lead_fields:
            self.doc.set("map_lead_fields", [])
            form_fields = []
            for lead in self.doc.table_hsya:
                questions = lead.questions
                if isinstance(questions, str):
                    questions = json.loads(questions)
                self.set_map_lead_fields(questions.get("questions", []), form_fields)

    def set_map_lead_fields(self, questions, form_fields):
        """Map form fields to lead fields."""
        field_type_mapping = {
            "EMAIL": "email",
            "FULL_NAME": "first_name",
            "PHONE": "mobile_no"
        }
        
        for question in questions:
            key = question.get("key")
            if key and key not in form_fields:
                question_type = question.get("type")
                lead_field = field_type_mapping.get(question_type, key)
                
                self.doc.append("map_lead_fields", {
                    "lead_field": lead_field,
                    "form_field": key,
                    "form_field_label": question.get("label"),
                    "form_field_type": question_type,
                })
                form_fields.append(key)

      
class ServerScript:
    """Handle server script creation for scheduled tasks."""
    
    def __init__(self, doc):
        self.doc = doc
        self.server_script = None
    
    def get_frappe_frequency(self):
        """Map custom frequencies to valid Frappe scheduler frequencies."""
        frequency_mapping = {
            "Every 5 Minutes": "Cron",
            "Every 10 Minutes": "Cron", 
            "Every 15 Minutes": "Cron",
            "Every 30 Minutes": "Cron"
        }
        return frequency_mapping.get(self.doc.event_frequency, self.doc.event_frequency)
    
    def get_cron_format(self):
        """Get cron format for minute-based frequencies."""
        cron_mapping = {
            "Every 5 Minutes": "*/5 * * * *",
            "Every 10 Minutes": "*/10 * * * *",
            "Every 15 Minutes": "*/15 * * * *",
            "Every 30 Minutes": "*/30 * * * *"
        }
        return cron_mapping.get(self.doc.event_frequency)
    
    def create_server_script(self):
        """Create server script for scheduled task execution."""
        script_name = str(self.doc.name).replace("-", "_").lower()
        script_data = {
            "doctype": "Server Script",
            "name": script_name,
            "script_type": "Scheduler Event",
            "event_frequency": self.get_frappe_frequency(),
            "module": "Mansico Meta Integration",
            "script": self.generate_script()
        }
        
        cron_format = self.get_cron_format()
        if cron_format:
            script_data["cron_format"] = cron_format
            
        self.server_script = frappe.get_doc(script_data)
    def generate_script(self):
        """Generate the script content for scheduled execution."""
        script_name = str(self.doc.name).replace("-", "_").lower()
        return (
            "from mansico_meta_integration.mansico_meta_integration.doctype.sync_new_add.sync_new_add import FetchLeads\n"
            "import frappe\n"
            f"fetch = FetchLeads('{script_name}')\n"
            "fetch.fetch_leads()\n"
        )
    


class RequestSendLead:
    """Handle sending lead data to Facebook API."""
    
    def __init__(self, request):
        self.request = request
    def send_lead(self, max_retries=3):
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.request.get_url, 
                    params=self.request.params, 
                    json=self.request.f_payload,
                    timeout=30  # 30 second timeout
                )
                _handle_api_error(response, self.request)
                return json.dumps(response.json())
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # Exponential backoff: 5, 10, 15 seconds
                    frappe.log_error("Facebook API Timeout - Retrying", f"Attempt {attempt + 1} timed out, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                else:
                    frappe.log_error("Facebook API Timeout - Final", f"All {max_retries} attempts timed out for URL: {self.request.get_url}")
                    return json.dumps({"error": "timeout", "message": f"Request timed out after {max_retries} attempts"})
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    frappe.log_error("Facebook API Network Error - Retrying", f"Attempt {attempt + 1} failed: {str(e)}, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                else:
                    frappe.log_error("Facebook API Network Error - Final", f"All {max_retries} attempts failed: {str(e)}")
                    return json.dumps({"error": "network_error", "message": str(e)})


class FetchLeads:
    def __init__(self, name):
        self.name = name

    @property
    def get_form_ids(self):
        form_ids = []
        for form in self.doc.table_hsya:
            form_ids.append(form.form_id)
        return form_ids

    @frappe.whitelist()
    def fetch_leads(self):
        self.doc = frappe.get_doc("Sync New Add", self.name)
        self.page = frappe.get_doc("Page ID", self.doc.page_id)
        self.form_ids = self.get_form_ids
        for form_id in self.form_ids:
            defaults = get_credentials()
            #  init Request
            request = Request(defaults.api_url, defaults.graph_api_version,
            self.doc.page_id, None, params={"fields": "access_token", "transport": "cors",
                    "access_token": defaults.access_token})
            # init RequestPageAccessToken
            request_page_access_token = RequestPageAccessToken(request)
            # get page access token
            request_page_access_token.get_page_access_token()
            # init Request
            request = Request(defaults.api_url, defaults.graph_api_version,
            form_id + "/leads", None, params={"access_token": request_page_access_token.page_access_token,
            "fields": "ad_id,ad_name,adset_id,adset_name,\
                campaign_id,campaign_name,created_time,custom_disclaimer_responses,\
                    field_data,form_id,id,home_listing,is_organic,partner_name,\
                        platform,post,retailer_item_id,vehicle"
                                              })
            # init RequestLeadGenForms
            request_lead_gen_forms = RequestLeadGenForms(request)
            # get lead forms
            request_lead_gen_forms.get_lead_forms()

            if request_lead_gen_forms.lead_forms.get("data"):
                # use self.lead_forms
                # fetch all leads then create them using create_lead
                # filter leads by created_time and id to avoid duplication
                self.paginate_lead_forms(request_lead_gen_forms.lead_forms)

                
            
    def paginate_lead_forms(self, lead_forms):
        if lead_forms.paging.get("next"):
            self.create_lead(lead_forms.get("data"))
            next_page = lead_forms.paging.get("next")
            try:
                response = requests.get(next_page, timeout=30)
                lead_forms = frappe._dict(response.json())
                return self.paginate_lead_forms(lead_forms)
            except requests.exceptions.Timeout:
                frappe.log_error("Pagination Timeout", f"Request timed out while paginating lead forms for URL: {next_page}")
                return lead_forms
            except requests.exceptions.RequestException as e:
                frappe.log_error("Pagination Network Error", f"Network error while paginating lead forms: {str(e)}")
                return lead_forms
        else:
            if lead_forms:
                self.create_lead(lead_forms.get("data"))
            return lead_forms
    def create_lead(self, leads):
        """Create leads in ERPNext from Facebook API data."""
        for lead in leads:
            lead_id = lead.get("id")
            if not lead_id:
                continue
            
            lead_data = {}
                
            try:
                # Check for existing lead within transaction
                existing_lead = frappe.db.get_value(
                    self.doc.lead_doctype_name, 
                    {"custom_meta_lead_id": lead_id}, 
                    "name"
                )
                
                if existing_lead:
                    continue
                
                # Map field data to lead fields
                for field in lead.get("field_data", []):
                    field_name = field.get("name")
                    field_values = field.get("values", [])
                    field_value = field_values[0] if field_values else None
                    
                    # Find mapping for this field
                    for mapping in self.doc.map_lead_fields:
                        if mapping.get("form_field") == field_name:
                            lead_data[mapping.get("lead_field")] = field_value
                            break

                # Create new lead document
                new_lead_data = {
                    "doctype": self.doc.lead_doctype_name,
                    "custom_meta_lead_id": lead_id,
                    "custom_lead_json": frappe._dict(lead),  
                }
                new_lead_data.update(lead_data)

                new_lead = frappe.get_doc(new_lead_data)
                
                try:
                    new_lead.insert(ignore_permissions=True)
                    frappe.db.commit()
                    
                    # Create lead in Facebook
                    try:
                        FetchLeads.create_lead_in_facebook(new_lead, self.page)
                    except Exception as fb_error:
                        frappe.log_error(
                            "Facebook Lead Creation Failed", 
                            f"Lead {new_lead.name} created successfully but Facebook sync failed: {str(fb_error)}"
                        )
                        
                except frappe.DuplicateEntryError:
                    # Handle duplicate entry error gracefully
                    frappe.db.rollback()
                    frappe.log_error(
                        "Duplicate Lead Prevented", 
                        f"Attempted to create duplicate lead with ID: {lead_id}"
                    )
                    continue

            except Exception as e:
                # Log errors and traceback for better debugging
                frappe.db.rollback()
                frappe.log_error("Lead Document Creation Failed", f"Failed to create Lead document from Facebook data: {str(e)}")
                frappe.log_error("Lead Creation Error Traceback", str(traceback.format_exc()))
                frappe.log_error("Failed Lead Data Context", f"Lead data that caused creation failure: {str(lead_data)}")

    
    @staticmethod
    def create_lead_in_facebook(lead, page):

        try:
            now = datetime.datetime.now()
            unixtime = int(now.timestamp())
            
            if not lead.custom_meta_lead_id:
                frappe.log_error("Facebook Lead Sync Validation Failed", f"Lead {lead.name} has no custom_meta_lead_id - cannot sync to Facebook")
                return
                
            if not hasattr(page, 'pixel_id') or not hasattr(page, 'pixel_access_token'):
                frappe.log_error("Facebook Page Configuration Error", f"Page {page.name if hasattr(page, 'name') else 'Unknown'} missing pixel_id or pixel_access_token - cannot sync lead to Facebook")
                return

            # Create UserData and CustomData objects
            user_data = UserData(lead.custom_meta_lead_id)
            custom_data = CustomData("crm", "ERP Next")

            # Create Payload object
            payload = Payload(
                event_name=lead.status,
                event_time=unixtime,
                action_source="system_generated",
                user_data=user_data,
                custom_data=custom_data
            )

            # Convert Payload to dictionary
            f_payload = {"data": [payload.to_dict()]}

            # Send request to Facebook
            defaults = get_credentials()
            request = Request(
                defaults.api_url,
                defaults.graph_api_version,
                page.pixel_id + "/events",
                f_payload,
                params={"access_token": page.pixel_access_token}
            )

            # Send the lead
            request_send_lead = RequestSendLead(request)
            response = request_send_lead.send_lead()

            # Insert a note with the response and payload
            note = frappe.get_doc({
                "doctype": "Note",
                "title": "Lead Created in Facebook Successfully",
                "public": 1,
                "content": (
                    f"Lead Created in Facebook Successfully for Lead: {lead.name}<br>"
                    f"Response: {str(response)}<br>"
                    f"Payload: {json.dumps(f_payload, indent=2)}"
                ),
            })
            note.insert(ignore_permissions=True)
            
        except Exception as e:
            frappe.log_error(
                "Error in Facebook Lead Creation",
                f"Failed to create Facebook lead for {lead.name}: {str(e)}\n\nTraceback: {frappe.get_traceback()}"
            )

class SyncNewAdd(Document):
    """Main document class for syncing Facebook leads."""
    
    def validate(self):
        """Validate and fetch forms from Facebook API."""
        defaults = get_credentials()
        #  init Request
        request = Request(defaults.api_url, defaults.graph_api_version,
         self.page_id, None, params={"fields": "access_token", "transport": "cors",
          "access_token": defaults.access_token})
        # init RequestPageAccessToken
        request_page_access_token = RequestPageAccessToken(request)
        # get page access token
        request_page_access_token.get_page_access_token()
        # init Request
        request = Request(defaults.api_url, defaults.graph_api_version,
         self.page_id + "/leadgen_forms", None, params={"access_token": request_page_access_token.page_access_token,
         "fields": "name,id,created_time,leads_count,page,page_id,\
         questions,leads {\
            ad_id,campaign_id,adset_id,campaign_name,ad_name,form_id,id,\
                adset_name,created_time\
                    }"})
        # init RequestLeadGenForms
        request_lead_gen_forms = RequestLeadGenForms(request)
        # get lead forms
        request_lead_gen_forms.get_lead_forms()
        # init AppendForms
        append_forms = AppendForms(request_lead_gen_forms.lead_forms, self)
        # append forms
        append_forms.append_forms()


    def check_email_id(self):
        first_name =  False
        for row in self.map_lead_fields:
            if row.lead_field == "first_name":
                first_name = True
        if not first_name:
            frappe.throw("Please map First Name Field")


    def _create_custom_field(self, fieldname, label, fieldtype, insert_after, unique=0):
        """Create a custom field if it doesn't exist."""
        if not frappe.get_meta(self.lead_doctype_name).has_field(fieldname):
            field_data = {
                "doctype": "Custom Field",
                "dt": self.lead_doctype_name,
                "fieldname": fieldname,
                "label": label,
                "fieldtype": fieldtype,
                "insert_after": insert_after,
                "read_only": 1,
            }
            
            if unique:
                field_data["unique"] = 1
                
            frappe.get_doc(field_data).insert(ignore_permissions=True)
    
    def check_meta_fields_found(self):
        self._create_custom_field("custom_meta_lead_id", "Custom Meta Lead ID", "Data", "name", unique=1)
        self._create_custom_field("custom_lead_json", "Custom Lead JSON", "Text", "custom_meta_lead_id")
        

        
    def on_submit(self):
        self.check_meta_fields_found()
        self.check_email_id()
        # i want to check if site hase enable_schedule = 1 
        # create Server Script
        # server_script = ServerScript(self)
        # server_script.create_server_script()
        # server_script.server_script.insert(ignore_permissions=True)
        # frappe.db.commit()
        # frappe.msgprint("Server Script Created Successfully")

    def on_cancel(self):
        pass
        # delete Server Script
        # frappe.delete_doc("Server Script", str(self.name).lower().replace("-","_"), ignore_permissions=True)
        # frappe.msgprint("Server Script Deleted Successfully")