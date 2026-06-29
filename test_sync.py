#!/usr/bin/env python
"""
Test script to create sample call details and test HubSpot sync
"""
import os
import sys
import django
from pathlib import Path
from datetime import datetime, date

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dubai_Client.settings')
django.setup()

from Client_app.models import call_details
from Client_app.hubspot_integration import sync_to_hubspot

def create_test_call_detail():
    """Create a test call detail record"""
    test_call = call_details.objects.create(
        uploader_name="Test Manager",
        name="John Doe",
        address="123 Test Street, Test City",
        phone_no="+1234567890",
        feedback="**Interested**",
        summary="Customer showed interest in the product. Wants to know more about pricing and features.",
        audio_flie="test_audio.mp3",
        month="January",
        download_file="https://example.com/test_audio.mp3",
        date=date.today(),
        time=datetime.now().time()
    )
    return test_call

def main():
    print("=== Testing HubSpot Sync with Sample Data ===")
    
    # Create test call detail
    print("Creating test call detail...")
    test_call = create_test_call_detail()
    print(f"Created call detail: {test_call.name} - {test_call.phone_no}")
    
    # Test sync
    print("\nTesting sync to HubSpot...")
    try:
        result = sync_to_hubspot(test_call)
        if result:
            print("SUCCESS: Call details synced to HubSpot!")
            print("Check your HubSpot CRM for the new contact.")
        else:
            print("FAILED: Could not sync to HubSpot")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    # Check if record was created
    print(f"\nTotal call details in database: {call_details.objects.count()}")
    
    # Cleanup (optional)
    cleanup = input("\nDo you want to delete the test record? (y/n): ")
    if cleanup.lower() == 'y':
        test_call.delete()
        print("Test record deleted.")

if __name__ == "__main__":
    main()