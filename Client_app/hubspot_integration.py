import requests
import json
import logging
from datetime import datetime
from django.conf import settings
from typing import Dict, Any, Optional
from .models import HubSpotConfig, OutboundLead
from django.utils import timezone 

logger = logging.getLogger(__name__)

class HubSpotCRMIntegration:
    """
    HubSpot CRM integration for sending call details to HubSpot CRM
    """


    def __init__(self):
        from .models import HubSpotConfig
        try:
            config = HubSpotConfig.objects.filter(is_active=True).first()
            if config:
                self.access_token = config.access_token
                self.portal_id = config.portal_id
            else:
                self.access_token = settings.HUBSPOT_ACCESS_TOKEN
                self.portal_id = settings.HUBSPOT_PORTAL_ID
        except:
            self.access_token = settings.HUBSPOT_ACCESS_TOKEN
            self.portal_id = settings.HUBSPOT_PORTAL_ID
        
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        self.last_contact_id = None

    def create_contact(self, call_detail) -> Optional[str]:
        """
        Create a new contact in HubSpot CRM
        
        Args:
            call_detail: call_details model instance
            
        Returns:
            str: Contact ID if successful, None otherwise
        """
        try:        
            contact_data = {
                "properties": {
                    "firstname": call_detail.name or "Unknown",
                    "phone": call_detail.phone_no,
                    "address": call_detail.address or "",
                    "lifecyclestage": self._get_lifecycle_stage(call_detail.feedback),
                    "hs_lead_status": self._get_lead_status(call_detail.feedback),
                    "lead_source": "AI Call System",
                    "lastname": call_detail.address or "",  
                    "hubspot_owner_id": self._get_owner_id()
                }
            }
            
            
            url = f"{self.base_url}/crm/v3/objects/contacts"
            response = requests.post(url, headers=self.headers, json=contact_data)

            if response.status_code == 201:
                contact_id = response.json().get("id")
                self.last_contact_id = contact_id
                logger.info(f"Successfully created contact in HubSpot: {contact_id}")
                return contact_id
            else:
                logger.error(f"Failed to create contact in HubSpot: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating contact in HubSpot: {str(e)}")


    def update_contact(self, contact_id: str, call_detail) -> bool:
        """
        Update an existing contact in HubSpot CRM
        
        Args:
            contact_id: HubSpot contact ID
            call_detail: call_details model instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            update_data = {
                "properties": {
                    "lifecyclestage": self._get_lifecycle_stage(call_detail.feedback),
                    "hs_lead_status": self._get_lead_status(call_detail.feedback),
                    "lastname": call_detail.address or "", 
                }
            }
            
            
            url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
            response = requests.patch(url, headers=self.headers, json=update_data)
            
            if response.status_code == 200:
                logger.info(f"Successfully updated contact in HubSpot: {contact_id}")
                return True
            else:
                logger.error(f"Failed to update contact in HubSpot: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating contact in HubSpot: {str(e)}")
            return False
    
    def find_contact_by_phone(self, phone_number: str) -> Optional[str]:
        """
        Find a contact by phone number
        
        Args:
            phone_number: Phone number to search for
            
        Returns:
            str: Contact ID if found, None otherwise
        """
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/search"
            search_data = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "phone",
                                "operator": "EQ",
                                "value": phone_number
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, headers=self.headers, json=search_data)
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    return results[0].get("id")
                    
        except Exception as e:
            logger.error(f"Error searching for contact in HubSpot: {str(e)}")
            
        return None
    
    def create_note(self, contact_id: str, call_detail) -> bool:
        """
        Create a note/activity for the contact
        
        Args:
            contact_id: HubSpot contact ID
            call_detail: call_details model instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            note_data = {
                "properties": {
                    "hs_note_body": self._format_call_note(call_detail),
                    "hs_timestamp": str(int(datetime.now().timestamp() * 1000)),  
                    "hubspot_owner_id": self._get_owner_id()
                },
                "associations": [
                    {
                        "to": {
                            "id": contact_id
                        },
                        "types": [
                            {
                                "associationCategory": "HUBSPOT_DEFINED",
                                "associationTypeId": 202
                            }
                        ]
                    }
                ]
            }
            
            url = f"{self.base_url}/crm/v3/objects/notes"
            response = requests.post(url, headers=self.headers, json=note_data)
            
            if response.status_code == 201:
                logger.info(f"Successfully created note for contact: {contact_id}")
                return True
            else:
                logger.error(f"Failed to create note: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating note in HubSpot: {str(e)}")
            return False
    
    def sync_call_details(self, call_detail) -> bool:
        """
        Main method to sync call details to HubSpot CRM
        
        Args:
            call_detail: call_details model instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Starting HubSpot sync for phone: {call_detail.phone_no}")
            logger.info(f"Call feedback: '{call_detail.feedback}' -> Lead Status: '{self._get_lead_status(call_detail.feedback)}', Lifecycle: '{self._get_lifecycle_stage(call_detail.feedback)}'")
            
            if not self.access_token:
                logger.error("HubSpot access token not configured")
                return False
                
            
            logger.info(f"Searching for existing contact with phone: {call_detail.phone_no}")
            contact_id = self.find_contact_by_phone(call_detail.phone_no)
            
            if contact_id:
                logger.info(f"Found existing contact {contact_id}, updating...")
                success = self.update_contact(contact_id, call_detail)
            else:
                logger.info(f"No existing contact found, creating new contact...")
                contact_id = self.create_contact(call_detail)
                success = contact_id is not None
            
           
            if success and contact_id:
                logger.info(f"Creating note for contact {contact_id}")
                self.create_note(contact_id, call_detail)
                logger.info(f"Successfully synced call details to HubSpot for {call_detail.phone_no}")
            else:
                logger.error(f"Failed to sync call details for {call_detail.phone_no}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error syncing call details to HubSpot: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _get_lifecycle_stage(self, feedback: str) -> str:
        """Map call feedback to HubSpot lifecycle stage"""
        if not feedback:
            return "subscriber"
            
        feedback_lower = feedback.lower().strip()
        
        if "interested" in feedback_lower and "not" not in feedback_lower:
            return "lead"
        elif "follow" in feedback_lower and "up" in feedback_lower:
            return "marketingqualifiedlead"
        elif "not" in feedback_lower and ("pick" in feedback_lower or "interested" in feedback_lower):
            return "subscriber"
        elif "no" in feedback_lower and "answer" in feedback_lower:
            return "subscriber"
        else:
            return "subscriber"
    
    def _get_lead_status(self, feedback: str) -> str:
        """Map call feedback to HubSpot lead status"""
        if not feedback:
            return "NEW"
            
        feedback_lower = feedback.lower().strip()
        
        if "interested" in feedback_lower and "not" not in feedback_lower:
            return "OPEN"
        elif "follow" in feedback_lower and "up" in feedback_lower:
            return "IN_PROGRESS"
        elif "not" in feedback_lower and ("pick" in feedback_lower or "interested" in feedback_lower):
            return "UNQUALIFIED"
        elif "no" in feedback_lower and "answer" in feedback_lower:
            return "ATTEMPTED_TO_CONTACT"
        else:
            return "NEW"
    
    def _get_owner_id(self) -> str:
        """Get default owner ID - you can customize this based on your needs"""
        return "" 
    
    def _format_call_note(self, call_detail) -> str:
        """Format call details into a note"""
        note = f"AI Call Record - {call_detail.date}\n"
        note += "=" * 40 + "\n\n"
        
        note += f"Phone: {call_detail.phone_no}\n"
        note += f"Name: {call_detail.name or 'N/A'}\n"
        note += f"Address: {call_detail.address or 'N/A'}\n"
        note += f"Status: {call_detail.feedback}\n"
        note += f"Time: {call_detail.time or 'N/A'}\n"
        note += f"Month: {call_detail.month or 'N/A'}\n"
        note += f"Manager: {call_detail.uploader_name or 'N/A'}\n\n"
        
        if call_detail.summary:
            note += f"Call Summary:\n{call_detail.summary}\n\n"
        
        if call_detail.download_file:
            note += f"Audio Recording: {call_detail.download_file}\n"
            
        note += "\n" + "=" * 40 + "\n"
        note += "Generated by AI Call CRM System"
            
        return note

    def get_all_contacts(self, limit: int = 100, after: str = None, since_timestamp: str = None) -> dict:
        """
        Get all contacts from HubSpot
        
        Args:
            limit: Number of contacts to fetch (max 100)
            after: Pagination cursor
            since_timestamp: ISO timestamp to fetch only updated contacts since this time
            
        Returns:
            dict: HubSpot API response
        """
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts"
            params = {
                'limit': limit,
                'properties': 'firstname,lastname,phone,email,hs_lead_status,lifecyclestage,createdate,lastmodifieddate'
            }
            
            if after:
                params['after'] = after
                
            # Add filter for recently modified contacts
            if since_timestamp:
                # Use search endpoint for filtering by modification date
                url = f"{self.base_url}/crm/v3/objects/contacts/search"
                search_data = {
                    "filterGroups": [
                        {
                            "filters": [
                                {
                                    "propertyName": "lastmodifieddate",
                                    "operator": "GTE",
                                    "value": since_timestamp
                                }
                            ]
                        }
                    ],
                    "properties": ['firstname', 'lastname', 'phone', 'email', 'hs_lead_status', 'lifecyclestage', 'createdate', 'lastmodifieddate'],
                    "limit": limit
                }
                
                if after:
                    search_data['after'] = after
                    
                response = requests.post(url, headers=self.headers, json=search_data)
            else:
                response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch contacts from HubSpot: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching contacts from HubSpot: {str(e)}")
            return {}

    def sync_contacts_from_hubspot(self, incremental: bool = True) -> int:
        """
        Sync contacts from HubSpot to local OutboundLead model
        
        Args:
            incremental: If True, only sync contacts modified since last sync
        
        Returns:
            int: Number of contacts synced
        """
        from .models import OutboundLead, HubSpotConfig
        from django.utils import timezone
        import datetime
        
        try:
            # Get the active HubSpot config
            config = HubSpotConfig.objects.filter(is_active=True).first()
            if not config:
                logger.error("No active HubSpot configuration found")
                return 0
            
            synced_count = 0
            updated_count = 0
            after = None
            since_timestamp = None
            
            # For incremental sync, use last sync timestamp
            if incremental and config.last_sync_timestamp:
                # Convert to HubSpot timestamp format (milliseconds since epoch)
                since_timestamp = str(int(config.last_sync_timestamp.timestamp() * 1000))
                logger.info(f"Performing incremental sync since {config.last_sync_timestamp}")
            else:
                logger.info("Performing full sync of all contacts")
            
            # Store current sync start time
            sync_start_time = timezone.now()
            
            while True:
                response = self.get_all_contacts(limit=100, after=after, since_timestamp=since_timestamp)
                
                if not response.get('results'):
                    break
                    
                for contact in response['results']:
                    try:
                        properties = contact.get('properties', {})
                        contact_id = contact.get('id')
                        
                        firstname = properties.get('firstname', '')
                        lastname = properties.get('lastname', '')
                        name = f"{firstname} {lastname}".strip() or 'Anonymous'
                        phone = properties.get('phone', '')
                        email = properties.get('email', '')
                        
                        if not phone and not email:
                            continue
                            
                        # Check if contact already exists by HubSpot ID first
                        existing_lead = OutboundLead.objects.filter(
                            hubspot_contact_id=contact_id,
                            source='hubspot'
                        ).first()
                        
                        # If not found by HubSpot ID, check by phone/email
                        if not existing_lead:
                            if phone:
                                existing_lead = OutboundLead.objects.filter(
                                    phone_number=phone,
                                    source='hubspot'
                                ).first()
                            
                            if not existing_lead and email:
                                existing_lead = OutboundLead.objects.filter(
                                    email=email,
                                    source='hubspot'
                                ).first()
                        
                        if existing_lead:
                            # Update existing lead
                            existing_lead.name = name
                            existing_lead.hubspot_contact_id = contact_id
                            if phone:
                                existing_lead.phone_number = phone
                            if email:
                                existing_lead.email = email
                            existing_lead.save()
                            updated_count += 1
                            logger.debug(f"Updated existing lead: {name} ({contact_id})")
                            
                        else:
                            # Create new lead
                            OutboundLead.objects.create(
                                name=name,
                                email=email or '',
                                phone_number=phone or '',
                                source='hubspot',
                                hubspot_contact_id=contact_id
                            )
                            synced_count += 1
                            logger.debug(f"Created new lead: {name} ({contact_id})")
                            
                    except Exception as e:
                        logger.error(f"Error processing contact {contact.get('id')}: {str(e)}")
                        continue
                
                # Check if there are more pages
                paging = response.get('paging', {})
                next_page = paging.get('next', {})
                after = next_page.get('after')
                
                if not after:
                    break
            
            # Update last sync timestamp
            config.last_sync_timestamp = sync_start_time
            config.save()
            
            logger.info(f"Successfully synced {synced_count} new contacts and updated {updated_count} existing contacts from HubSpot")
            return synced_count
            
        except Exception as e:
            logger.error(f"Error syncing contacts from HubSpot: {str(e)}")
            return 0


def sync_to_hubspot(call_detail) -> bool:
    hubspot = HubSpotCRMIntegration()
    ok = hubspot.sync_call_details(call_detail)

    if ok:
        
        lead, created = OutboundLead.objects.update_or_create(
            hubspot_contact_id=hubspot.last_contact_id,     
            defaults={
                "name": call_detail.name or "",
                "phone_number": call_detail.phone_no or "",
                "email": getattr(call_detail, "email", ""),
                "source": "hubspot",
                "created_at": timezone.now(),
            },
        )
        logger.info(
            "OutboundLead %s (id=%s) in DB for HubSpot contact %s",
            "created" if created else "updated",
            lead.id,
            hubspot.last_contact_id,
        )
    return ok


def sync_from_hubspot():
    """
    Convenience function to sync contacts from HubSpot to local database
    
    Returns:
        int: Number of contacts synced
    """
    hubspot = HubSpotCRMIntegration()
    return hubspot.sync_contacts_from_hubspot()