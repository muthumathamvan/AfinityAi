from django.core.management.base import BaseCommand
from Client_app.models import call_details as CallDetails
from Client_app.hubspot_integration import sync_to_hubspot 
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Sync all call details to HubSpot"

    def handle(self, *args, **kwargs):
        call_records = CallDetails.objects.all()  
        total = call_records.count()
        success_count = 0

        self.stdout.write(f"Syncing {total} call records to HubSpot...")

        for i, record in enumerate(call_records, 1):
            self.stdout.write(f"[{i}/{total}] Syncing {record.phone_no}...")
            success = sync_to_hubspot(record)
            if success:
                success_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Synced {success_count}/{total} records successfully."))
