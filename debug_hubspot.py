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
import requests

def main():
    print("HubSpot Integration Debug Tool")
    print("=" * 50)
    
    # Test configuration
    print("=== Configuration ===")
    print(f"HUBSPOT_ACCESS_TOKEN: {'SET' if settings.HUBSPOT_ACCESS_TOKEN else 'NOT SET'}")
    print(f"HUBSPOT_PORTAL_ID: {settings.HUBSPOT_PORTAL_ID if settings.HUBSPOT_PORTAL_ID else 'NOT SET'}")
    print()
    
    # Test API connection
    print("=== API Connection Test ===")
    try:
        hubspot = HubSpotCRMIntegration()
        url = f"{hubspot.base_url}/crm/v3/objects/contacts"
        response = requests.get(url + "?limit=1", headers=hubspot.headers)
        
        print(f"API Response Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: HubSpot API connection working")
            data = response.json()
            print(f"Found {len(data.get('results', []))} contacts")
        else:
            print(f"FAILED: HubSpot API connection failed: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Connection error: {str(e)}")
    print()
    
    # Test with existing data
    print("=== Testing Sync with Existing Data ===")
    try:
        latest_call = call_details.objects.first()
        if latest_call:
            print(f"Testing sync with call: {latest_call.phone_no}")
            print(f"Name: {latest_call.name}")
            print(f"Feedback: {latest_call.feedback}")
            print(f"Date: {latest_call.date}")
            
            result = sync_to_hubspot(latest_call)
            if result:
                print("SUCCESS: Sync completed")
            else:
                print("FAILED: Sync failed")
        else:
            print("No call details found in database")
    except Exception as e:
        print(f"ERROR: Sync error: {str(e)}")
    print()
    
    # Test creating a contact
    print("=== Testing Direct Contact Creation ===")
    try:
        hubspot = HubSpotCRMIntegration()
        
        contact_data = {
            "properties": {
                "firstname": "Test Contact",
                "phone": "+1234567890",
                "lifecyclestage": "lead"
            }
        }
        
        url = f"{hubspot.base_url}/crm/v3/objects/contacts"
        response = requests.post(url, headers=hubspot.headers, json=contact_data)
        
        print(f"Create Contact Response: {response.status_code}")
        if response.status_code == 201:
            print("SUCCESS: Test contact created")
            contact_id = response.json().get("id")
            print(f"Contact ID: {contact_id}")
        else:
            print(f"FAILED: Could not create test contact: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Error creating test contact: {str(e)}")

if __name__ == "__main__":
    main()