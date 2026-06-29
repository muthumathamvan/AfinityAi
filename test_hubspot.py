#!/usr/bin/env python
"""
Debug script to test HubSpot integration
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dubai_Client.settings')
django.setup()

from Client_app.models import call_details
from Client_app.hubspot_integration import HubSpotCRMIntegration, sync_to_hubspot
from django.conf import settings

def test_hubspot_config():
    """Test HubSpot configuration"""
    print("=== HubSpot Configuration Test ===")
    print(f"HUBSPOT_ACCESS_TOKEN: {'*' * 10 if settings.HUBSPOT_ACCESS_TOKEN else 'NOT SET'}")
    print(f"HUBSPOT_PORTAL_ID: {settings.HUBSPOT_PORTAL_ID if settings.HUBSPOT_PORTAL_ID else 'NOT SET'}")
    print()

def test_hubspot_connection():
    """Test HubSpot API connection"""
    print("=== HubSpot API Connection Test ===")
    try:
        hubspot = HubSpotCRMIntegration()
        
        # Test basic API connection by searching for a contact
        import requests
        url = f"{hubspot.base_url}/crm/v3/objects/contacts"
        response = requests.get(url + "?limit=1", headers=hubspot.headers)
        
        print(f"API Response Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ HubSpot API connection successful")
            data = response.json()
            print(f"Found {len(data.get('results', []))} contacts")
        else:
            print(f"❌ HubSpot API connection failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
    print()

def test_sync_with_existing_data():
    """Test sync with existing call details"""
    print("=== Testing Sync with Existing Data ===")
    
    # Get the latest call detail
    latest_call = call_details.objects.first()
    if latest_call:
        print(f"Testing sync with call: {latest_call.phone_no}")
        print(f"Name: {latest_call.name}")
        print(f"Feedback: {latest_call.feedback}")
        print(f"Date: {latest_call.date}")
        
        try:
            result = sync_to_hubspot(latest_call)
            if result:
                print("✅ Sync successful")
            else:
                print("❌ Sync failed")
        except Exception as e:
            print(f"❌ Sync error: {str(e)}")
    else:
        print("No call details found in database")
    print()

def test_create_contact():
    """Test creating a contact directly"""
    print("=== Testing Direct Contact Creation ===")
    try:
        hubspot = HubSpotCRMIntegration()
        
        # Create a test contact
        contact_data = {
            "properties": {
                "firstname": "Test Contact",
                "phone": "+1234567890",
                "lifecyclestage": "lead"
            }
        }
        
        import requests
        url = f"{hubspot.base_url}/crm/v3/objects/contacts"
        response = requests.post(url, headers=hubspot.headers, json=contact_data)
        
        print(f"Create Contact Response: {response.status_code}")
        if response.status_code == 201:
            print("✅ Test contact created successfully")
            contact_id = response.json().get("id")
            print(f"Contact ID: {contact_id}")
        else:
            print(f"❌ Failed to create test contact: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating test contact: {str(e)}")
    print()

if __name__ == "__main__":
    print("HubSpot Integration Debug Tool")
    print("=" * 50)
    
    test_hubspot_config()
    test_hubspot_connection()
    test_sync_with_existing_data()
    test_create_contact()