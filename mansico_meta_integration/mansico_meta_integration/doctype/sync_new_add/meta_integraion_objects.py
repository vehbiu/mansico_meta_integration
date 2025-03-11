class UserData:
    def __init__(self, lead_id):
        self.lead_id = lead_id

    def to_dict(self):
        return {
            "lead_id": self.lead_id
        }
    
class CustomData:
    def __init__(self, event_source, lead_event_source):
        self.event_source = event_source
        self.lead_event_source = lead_event_source

    def to_dict(self):
        return {
            "event_source": self.event_source,
            "lead_event_source": self.lead_event_source
        }
class Payload:
    def __init__(self, event_name, event_time, action_source, user_data, custom_data):
        self.event_name = event_name
        self.event_time = event_time
        self.action_source = action_source
        self.user_data = user_data
        self.custom_data = custom_data

    def to_dict(self):
        return {
            "event_name": self.event_name,
            "event_time": self.event_time,
            "action_source": self.action_source,
            "user_data": self.user_data.to_dict(),
            "custom_data": self.custom_data.to_dict()
        }