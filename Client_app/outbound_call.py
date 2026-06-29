from django.shortcuts import render
from django.http import JsonResponse
from .models import OutboundLead, BookMeeting, RateUs
from elevenlabs import ElevenLabs
from postmarker.core import PostmarkClient
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def outbound_call_form(request):
    if request.method == 'POST':
       
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format'}, status=400)
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            phone_number = data.get('phone_number', '').strip()
        else:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()

        
        if not name or not email or not phone_number:
            error_msg = 'All fields (Name, Email, Phone Number with Country Code) are required.'
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'error': error_msg}, status=400)
            return render(request, 'index.html', {'error': error_msg})

        
        lead = OutboundLead.objects.create(
            name=name,
            email=email,
            phone_number=phone_number
        )

        
        try:
            client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

            response = client.conversational_ai.twilio.outbound_call(
                agent_id=settings.ELEVENLABS_AGENTS,
                agent_phone_number_id=settings.AGENT_PHONE_NUMBER_ID,
                to_number=phone_number
            )
            
            print("raw response:", response)

            conversation_id = None
            if isinstance(response, dict):
                conversation_id = response.get("conversation_id")
            else:
                conversation_id = getattr(response, "conversation_id", None)

            if not conversation_id:
                raise ValueError(f"no conversation_id returned. raw response: {response}")

            lead.conversation_id = response.conversation_id
            lead.save()

            success_data = {
                'message': f'Call successfully triggered to {phone_number}',
                'conversation_id': response.conversation_id,
                'lead_id': lead.id
            }

            if request.headers.get('Content-Type') == 'application/json':
                success_data['status'] = 'success'
                return JsonResponse(success_data)
            print("Call initiated successfully:", success_data)
            return render(request, 'index.html', success_data)

        except Exception as e:
            error_msg = f'Failed to initiate call: {str(e)}'
            print("Error during call:", e)

            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'error': error_msg}, status=500)

            return render(request, 'index.html', {'error': error_msg})

    
    return render(request, 'index.html')


@csrf_exempt
def book_meeting(request):
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format'}, status=400)
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            company = data.get('company', '').strip()
            message = data.get('message', '').strip()

        else:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()            
            company = request.POST.get('company', '').strip()
            message = request.POST.get('message', '').strip()

        if not name or not email or not phone or not company:
            error_msg = 'All fields (Name, Email, Phone , Company) are required.'
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'error': error_msg}, status=400)
            return render(request, 'index.html', {'error': error_msg})
        
        lead = BookMeeting.objects.create(
            name=name,
            email=email,
            phone=phone,
            company=company,
            message=message
        )

        try:
            client = PostmarkClient(server_token=settings.POSTMARK_API_TOKEN)

            client.emails.send(
                To= settings.POSTMARK_RECIPIENT_EMAIL,
                From=settings.POSTMARK_SENDER_EMAIL,
                Subject=f"Meeting Request from {name}, {company}",
                HtmlBody=f"""
                <p>Hi,</p>
                <p>You have a new meeting request from {name} ({email}).</p>
                <p>Phone: {phone}</p>
                <p>Company: {company}</p>
                <p>Message: {message}</p>
                <p>Best regards,</p>
                <p>Dubai Client Team</p>
                """
            )

            print ("response for Postmark:", client)

            lead.save()

            success_data = {
                'message': f'Meeting successfully booked with {name}',
            }

            if request.headers.get('Content-Type') == 'application/json':
                success_data['status'] = 'success'
                return JsonResponse(success_data)
            print("Meeting booked successfully:", success_data)
            return render(request, 'index.html', success_data)
       
        except Exception as e:
            error_msg = f'Failed to send email: {str(e)}'
            print("Error during email sending:", e)

            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'error': error_msg}, status=500)
            
            return render(request, 'index.html', {'error': error_msg})
        
    return render(request, 'index.html')

@csrf_exempt
def rate_us(request):
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format'}, status=400)
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            rating = data.get('rating', 0)
            feedback = data.get('feedback', '').strip()

        else:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            rating = request.POST.get('rating', 0)
            feedback = request.POST.get('feedback', '').strip()

        if not name or not email or not rating:
            error_msg = "Name, Email and Rating are required."
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'error': error_msg}, status=400)

        rate = RateUs.objects.create(
            name=name,
            email=email,
            rating=rating,
            feedback=feedback
        )
        
        rate.save()
        print("Rating saved successfully:", rate)

        success_data = {
            'message': f'Thank you for your feedback, {name}!',
            'email': email,
            'rating': rating,
            'feedback': feedback
        }

        if request.headers.get('Content-Type') == 'application/json':
            success_data['status'] = 'success'
            return JsonResponse(success_data)
        print("Feedback received successfully:", success_data)

        return render(request, 'index.html', success_data)
    return render(request, 'index.html')
    