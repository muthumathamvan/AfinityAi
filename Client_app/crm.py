from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.shortcuts import render
from .models import call_details, OutboundLead
from datetime import datetime
from django.utils import timezone

def crm_dashboard(request):
    agent_id = request.GET.get("agent_id")
    feedback_filter = request.GET.get("feedback", "")
    sort_by = request.GET.get("sort", "-date")
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")
    source_filter = request.GET.get("source", "")

    # Get call details (existing functionality)
    call_details_queryset = call_details.objects.filter(
        Q(feedback="**Interested**") | Q(feedback="**Follow up**")
    )

    if agent_id:
        call_details_queryset = call_details_queryset.filter(uploader_name=agent_id)

    if feedback_filter:
        call_details_queryset = call_details_queryset.filter(feedback=feedback_filter)
    
    if date_from:
        call_details_queryset = call_details_queryset.filter(date__gte=parse_date(date_from))
    if date_to:
        call_details_queryset = call_details_queryset.filter(date__lte=parse_date(date_to))

    # Get HubSpot leads
    hubspot_leads_queryset = OutboundLead.objects.filter(source='hubspot')
    
    if date_from:
        hubspot_leads_queryset = hubspot_leads_queryset.filter(created_at__date__gte=parse_date(date_from))
    if date_to:
        hubspot_leads_queryset = hubspot_leads_queryset.filter(created_at__date__lte=parse_date(date_to))

    # Convert querysets to lists for combining
    clients_list = []
    
    # Add call details to the list
    for call in call_details_queryset:
        clients_list.append({
            'type': 'call_detail',
            'id': call.id,
            'name': call.name or 'N/A',
            'phone_no': call.phone_no,
            'address': call.address or 'N/A',
            'date': call.date,
            'feedback': call.feedback,
            'summary': call.summary or 'N/A',
            'uploader_name': call.uploader_name or 'N/A',
            'audio_url': call.audio_url,
            'source': 'dashboard',
            
            'created_at': timezone.make_aware(datetime.combine(call.date, call.time if call.time else datetime.min.time())),
        })
    
    # Add HubSpot leads to the list
    for lead in hubspot_leads_queryset:
        clients_list.append({
            'type': 'hubspot_lead',
            'id': lead.id,
            'name': lead.name,
            'phone_no': lead.phone_number,
            'address': 'N/A',  
            'date': lead.created_at.date(),
            'feedback': 'HubSpot Lead',
            'summary': f'Lead synced from HubSpot (Contact ID: {lead.hubspot_contact_id})',
            'uploader_name': 'HubSpot Sync',
            'audio_url': None,
            'source': 'hubspot',
            'created_at': lead.created_at,
        })
    
    # Apply source filter
    if source_filter:
        clients_list = [client for client in clients_list if client['source'] == source_filter]
    
    # Sort the combined list
    if sort_by == "-date":
        clients_list.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "date":
        clients_list.sort(key=lambda x: x['created_at'])
    elif sort_by == "name":
        clients_list.sort(key=lambda x: x['name'].lower())
    elif sort_by == "feedback":
        clients_list.sort(key=lambda x: x['feedback'])

    return render(request, "crm_dashboard.html", {
        "clients": clients_list,
        "agent_id": agent_id,
        "source_filter": source_filter,
        "total_count": len(clients_list),
        "hubspot_count": len([c for c in clients_list if c['source'] == 'hubspot']),
        "dashboard_count": len([c for c in clients_list if c['source'] == 'dashboard']),
    })
