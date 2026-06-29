from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('user', 'Normal User'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    user_under = models.CharField(max_length=20, blank= True, null= True)

    def __str__(self):
        return f"{self.username} - {self.role}"

class BusinessDetails(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business"
    )

    company_name = models.CharField(max_length=255)
    company_email = models.EmailField()
    company_phone = models.CharField(max_length=20)
    company_address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.owner.username}"
    
# ===============================
# TENANT
# ===============================
class Tenant(models.Model):

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tenant"
    )

    tenant_id = models.CharField(max_length=100, unique=True)
    tenant_name = models.CharField(max_length=255)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tenant_name


# ===============================
# BRANCH
# ===============================
class Branch(models.Model):

    PLAN_CHOICES = (
        ('Trial', 'Trial'),
        ('Standard', 'Standard'),
    )

    BOOLEAN_CHOICES = (
        (True, 'True'),
        (False, 'False'),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="branches"
    )

    name = models.CharField(max_length=255)
    branch_code = models.CharField(max_length=50, unique=True)

    classification = models.CharField(max_length=100, blank=True, null=True)

    start_date = models.DateField()
    end_date = models.DateField()

    plan_type = models.CharField(
        max_length=50,
        choices=PLAN_CHOICES
    )

    # New Fields Added 👇
    brn = models.CharField(max_length=100, blank=True, null=True)
    sst_number = models.CharField(max_length=100, blank=True, null=True)
    industry_code = models.CharField(max_length=100, blank=True, null=True)
    business_activity = models.TextField(blank=True, null=True)

    clinic_header = models.BooleanField(default=False)
    controlled_medicine = models.BooleanField(default=False)
    dental_module = models.BooleanField(default=False)

    mi2u_expiry = models.DateField(blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# ===============================
# DEPARTMENT
# ===============================
class Department(models.Model):

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="departments"
    )

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


# ===============================
# WAREHOUSE
# ===============================
class Warehouse(models.Model):

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="warehouses"
    )

    warehouse_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)

    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name



class call_details(models.Model):
    uploader_name = models.CharField(max_length=30, null=True)
    name = models.CharField(max_length=30, null=True)
    address = models.TextField(null=True)
    phone_no = models.CharField(max_length=30, null=True)
    feedback = models.CharField(max_length=20, null=True)
    summary = models.TextField(null=True)
    audio_flie = models.CharField(max_length=255)
    audio_url = models.FileField(upload_to='audios/')
    month= models.CharField(max_length=30, null=True)
    download_file = models.URLField(max_length=500)
    date = models.DateField(default=date.today)
    time = models.TimeField(null=True, blank=True)
    user_data =models.CharField(max_length=30, null=True)

class inboundcalls(models.Model):
    agent_id = models.CharField(max_length=100)
    conversation_id = models.CharField(max_length=100)
    summary = models.TextField(blank=True, null=True)
    external_number = models.CharField(max_length=20)
    direction = models.CharField(max_length=10)
    call_datetime = models.CharField(max_length=100)
    audio_url = models.FileField(upload_to='audios/')
    user_data =models.CharField(max_length=30, null=True)

class OutboundLead(models.Model):
    name = models.CharField(max_length=255, null=False, default='Anonymous')
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    conversation_id = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=50, default='dashboard', help_text='lead (dashboard, hubspot)')
    hubspot_contact_id = models.CharField(max_length=50, blank=True, null=True, help_text='HubSpot Contact ID if synced from HubSpot')
    created_at = models.DateTimeField(auto_now_add=True)
    user_data =models.CharField(max_length=30, null=True)

    def __str__(self):
        return f"{self.name} - {self.phone_number}"

class HubSpotConfig(models.Model):
    access_token = models.CharField(max_length=500)
    portal_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync_timestamp = models.DateTimeField(null=True, blank=True, help_text='sync from HubSpot')
    is_active = models.BooleanField(default=True)
    user_data =models.CharField(max_length=30, null=True)

    class Meta:
        db_table = 'hubspot_config'

    def __str__(self):
        return f"HubSpot Config - Portal: {self.portal_id}"


class BookMeeting(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_data =models.CharField(max_length=30, null=True)

    def __str__(self):
        return f"Meeting with {self.name} - {self.phone}"

class RateUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    rating = models.IntegerField(default=0, help_text='Rating from 1 to 5')
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_data =models.CharField(max_length=30, null=True)

    def __str__(self):
        return f"Rating by {self.name} - {self.rating}/5"

class WidgetCalls(models.Model):
    agent_id = models.CharField(max_length=255)
    conversation_id = models.CharField(max_length=255, unique=True)
    summary = models.TextField(blank=True)
    call_datetime = models.DateTimeField(null=True, blank=True)
    call_time = models.CharField(max_length=100)
    audio_url = models.URLField(blank=True, null=True)
    audio_file = models.FileField(upload_to="widget_recordings/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_data =models.CharField(max_length=30, null=True)

# models.py
class ElevenCall(models.Model):
    conversation_id = models.CharField(max_length=120, unique=True)
    agent_id = models.CharField(max_length=120)
    direction = models.CharField(max_length=20, null=True, blank=True)
    
    call_date = models.DateField(null=True, blank=True)
    call_time = models.TimeField(null=True, blank=True)
    
    summary = models.TextField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    audio_url = models.URLField(null=True, blank=True)

    audio_file = models.FileField(upload_to="call_audio/", null=True, blank=True)
    has_audio = models.BooleanField(default=False)

    raw_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    user_data =models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.conversation_id
    
class AIAssistant(models.Model):
    agent_name = models.CharField(max_length=255, null=True, blank=True)
    primary_language = models.CharField(max_length=100)
    secondary_languages = models.CharField(max_length=255, blank=True, null=True)

    system_prompt = models.TextField()

    tenant_id = models.CharField(max_length=100, null=True, blank=True)
    branch_id = models.CharField(max_length=100, null=True, blank=True)

    voice_name = models.CharField(max_length=100, null=True, blank=True)
    agent_id = models.CharField(max_length=100, null=True, blank=True)
    voice_id = models.CharField(max_length=100, null=True, blank=True)
    widget_code = models.TextField()

    uploaded_file = models.FileField(
        upload_to="assistant_files/",
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.agent_name

