from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Count, F
from rest_framework.permissions import IsAuthenticated, AllowAny 
from dateutil.relativedelta import relativedelta
from EMI_app.models import plot_details, CustomUser, EMIOption, PlotPurchase, EMIPayment, EMIUser
from django.db import transaction
from django.utils import timezone
from EMI_app.serializer import RegisterSerializer, LoginSerializer, EMIUserSerializer 
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from dotenv import load_dotenv
from twilio.rest import Client
from razorpay import Client
from datetime import timedelta, datetime, time
import razorpay
from razorpay.errors import SignatureVerificationError
import hmac
import hashlib
import os 
import time as time_module

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

User = get_user_model()

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_cities(request):
    cities = plot_details.objects.values('city').distinct()
    city_list = [city['city'] for city in cities]

    return JsonResponse({
        'cities': city_list,
        'count': len(city_list)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_projects_by_city(request):
    city_name = request.data.get('city')
    project_id = request.data.get('project_id')

    if not city_name:
        return JsonResponse({'error': 'City is required'}, status=status.HTTP_400_BAD_REQUEST)

    projects = plot_details.objects.filter(
        city__iexact=city_name
    ).values('city','project_id','project').annotate(total_plots=Count('plot_id')).distinct()
    
    if not projects.exists():
        return JsonResponse({'error': 'No projects found for this city'}, status=status.HTTP_404_NOT_FOUND)
    
    project_list = [project['project'] for project in projects]
    

    if not project_list:
        return JsonResponse({'error': 'No projects found for this city'}, status=status.HTTP_404_NOT_FOUND)

    project_data = [
        {
            'city': project['city'],
            'project_id': project['project_id'],
            'project_name': project['project'],
            'total_plots': project['total_plots']
        }
        for project in projects
    ]

    return JsonResponse({
        'projects': project_data,
        'count': len(project_list)
        
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllowAny])
def get_plots_by_project(request):
    project_id = request.data.get('project_id')

    if not project_id:
        return JsonResponse({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    plots = plot_details.objects.filter(project_id=project_id)

    if not plots.exists():
        return JsonResponse({'error': 'No plots found for this project'}, status=status.HTTP_404_NOT_FOUND)

    plot_data = [
        {
            'plot_id': plot.plot_id,
            'plot_no': plot.plot_no,
            'sqft_area': plot.sqft_area,
            'facing': plot.facing,
            'price_in_no': plot.price_in_no,
            'price_in_words': plot.price_in_words,
            'status': plot.status
        }
        for plot in plots
    ]

    return JsonResponse({
        'project_id': project_id,
        'project_name': plots.first().project if plots.exists() else None,
        'plots': plot_data,
        'count': len(plot_data)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def select_plot(request):
    plot_id = request.data.get('plot_id')

    if not plot_id:
        return JsonResponse({'error': 'plot_no and project_id are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        plot = plot_details.objects.get(plot_id=plot_id)
    except plot_details.DoesNotExist:
        return JsonResponse({'error': 'Plot not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if plot.status != 'Available':
        return JsonResponse({'error': 'Plot is not available'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    plot.status = 'reserved'
    plot.save()
    request.session['selected_plot_id'] = plot.plot_id

    return JsonResponse({
        'message': f'Plot {plot_id} reserved. Please login/register to continue.',
        'selected_plot_id': plot.plot_id
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def check_reserved_plot(request):
    plot_no = request.data.get('plot_no')
    project = request.data.get('project')

    if not plot_no and not project:
        return JsonResponse({'error': 'Plot number is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        plot = plot_details.objects.get(plot_no=plot_no, project=project)
        if plot.status == 'reserved':
            return JsonResponse({'message': 'Plot is reserved'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Plot is available'}, status=status.HTTP_200_OK)
        
    except plot_details.DoesNotExist:
        return JsonResponse({'error': 'Plot not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, username=email, password=password)  

        if not user:
            return JsonResponse({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token.set_exp(lifetime=timedelta(days=1))

        return JsonResponse({
            "message": "Login successful",
            "bearer": str(access_token),
            "user": {
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number
            }
        }, status=status.HTTP_200_OK)
    
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_selected_plot_after_login(request):
    selected_plot_id = request.session.get('selected_plot_id')

    if not selected_plot_id:
        return JsonResponse({'error': 'No plot selected'}, status=status.HTTP_404_NOT_FOUND)

    try:
        plot = plot_details.objects.get(plot_id=selected_plot_id)
    except plot_details.DoesNotExist:
        return JsonResponse({'error': 'Selected plot not found'}, status=status.HTTP_404_NOT_FOUND)

    return JsonResponse({
        'plot_id': plot.plot_id,
        'plot_no': plot.plot_no,
        'sqft_area': plot.sqft_area,
        'facing': plot.facing,
        'price_in_no': plot.price_in_no,
        'price_in_words': plot.price_in_words,
        'status': plot.status,
        'project_id': plot.project_id,
        'project_name': plot.project,
        'city': plot.city
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    plot_id = request.data.get('plot_id') 

    if not plot_id:
        return JsonResponse({'error': 'plot_id is required'}, status=status.HTTP_400_BAD_REQUEST)
 
    plot = plot_details.objects.filter(plot_id=plot_id).first()
    if not plot:
        return JsonResponse({'error': 'Plot not found'}, status=status.HTTP_404_NOT_FOUND)


    response_data = {
        'message': f'User dashboard accessed for plot {plot_id}',
        'plot_id': plot_id,
        'project': plot.project,
        'city': plot.city,
        'status': plot.status,
        'price_in_no': plot.price_in_no,
        'price_in_words': plot.price_in_words,
        'sqft_area': plot.sqft_area,
        'facing': plot.facing,
        'plot_no': plot.plot_no,
       
    }

    return JsonResponse(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def buy_plot_full(request):
    selected_plot_id = request.data.get('plot_id')
    
    if not selected_plot_id:
        return JsonResponse({'error':'No plot selected'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        plot = plot_details.objects.get(plot_id=selected_plot_id)
        
        
        total_price = 10
        upfront_amount = 10 * 100
        emi_amount = 0 
        

        order_data = {
            'amount':upfront_amount,
            'currency': 'INR',
            'receipt': f"plot_{plot.plot_id}_purchased_receipt_{int(time_module.time())}"
            
        }

        order = razorpay_client.order.create(data=order_data)

        plot_purchase = PlotPurchase.objects.create(
            
            customer=request.user,
            plot=plot,
            payment_type='full',
            total_amount=total_price,
            down_payment=upfront_amount,
            emi_amount=emi_amount,
            status='pending',
            emi_option=None
        
        )

        return JsonResponse({
            'message': 'plot purchased successfully',
            'razorpay_order': order,
            'plot_purchase_id': plot_purchase.id,
            'total_amount': total_price,
            'status': plot_purchase.status,
            'upfront_amount': upfront_amount,
        })
    
    except plot_details.DoesNotExist:
        return JsonResponse({'error': 'failed to purchase plot'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_emi_options(request):
    plot_id = request.GET.get('plot_id')

    if not plot_id:
        return JsonResponse({'error': 'plot_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        plot = plot_details.objects.get(plot_id=plot_id)
        price = plot.price_in_no

        upfront_amount = price * 0.5
        months_options = [12, 24, 36]

        emi_options = []
        for m in months_options:
            emi_amount = (price - upfront_amount) / m
            emi_options.append({
                'duration_months': m,
                'interest_rate': 0,
                'upfront_amount': round(upfront_amount, 2),
                'emi_amount': round(emi_amount, 2),
                'total_payable': round(upfront_amount + (emi_amount * m), 2)
            })

        return JsonResponse({
            'plot_id': plot.plot_id,
            'price_in_no': price,
            'upfront_amount': upfront_amount,
            'emi_options': emi_options,
            'count': len(emi_options),
        })

    except plot_details.DoesNotExist:
        return JsonResponse({'error': 'Invalid plot_id'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def emi_plans(request):
    plot_id = request.data.get('plot_id')
    months = int(request.data.get('months', 0))
    

    if months not in [12, 24, 36]:
        return JsonResponse({'error': 'Invalid EMI months. Choose from 12, 24, or 36 months.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        plot = plot_details.objects.get(plot_id=plot_id)
        price = plot.price_in_no

    except plot_details.DoesNotExist:
        return JsonResponse({'error': 'Plot not found'}, status=status.HTTP_404_NOT_FOUND)

    
    upfront_amount = price * 0.5
    emi_amount = (price - upfront_amount) / months

    emi_schedule = []
    base_date = timezone.localtime(timezone.now()).date()  
    for i in range(1, months + 1):
        due_date = timezone.make_aware(
            datetime.combine(base_date, time(9, 0))
        ) + relativedelta(months=i)

        emi_schedule.append({
            "emi_number": i,
            "amount": round(emi_amount, 2),
            "due_date": due_date.isoformat()
        })

    result = {
        'plot_id': plot.plot_id,
        'price_in_no': price,
        'upfront_amount': round(upfront_amount, 2),
        'emi_amount': round(emi_amount, 2),
        'months': months,
        'emi_options': emi_schedule
    }
    return JsonResponse({ 'success': True, 'emi_plan': result}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def save_emi_user_info(request):
    user = request.user
    plot_id = request.data.get('plot_id')
    months = int(request.data.get('months', 0))

    if months not in [12, 24, 36]:
        return JsonResponse({'error': 'Invalid EMI months. Choose from 12, 24, or 36 months.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        try:
            plot = plot_details.objects.get(plot_id=plot_id)
        except plot_details.DoesNotExist:
            return JsonResponse({'error': 'Plot not found'}, status=status.HTTP_404_NOT_FOUND)
        
        price = plot.price_in_no
        upfront_amount = price * 0.5
        emi_amount = (price - upfront_amount) / months

        emi_schedule = []
        base_date = timezone.localtime(timezone.now()).date()

        for i in range(1, months +1):
            due_date = timezone.make_aware(
                datetime.combine(base_date, time(9, 0))
            ) + relativedelta(months=i)

            emi_schedule.append({
                "emi_number": i,
                "amount": round(emi_amount, 2),
                "due_date": due_date.isoformat()
            })

        try:
            emi_user = EMIUser.objects.get(user=user)
            serializer = EMIUserSerializer(emi_user, data=request.data, partial=True)
        except EMIUser.DoesNotExist:
            serializer = EMIUserSerializer(data=request.data)

        if serializer.is_valid():
            emi_user = serializer.save(user=user)  
            return Response({
                "success": True,
                "message": "EMI user information saved successfully",
                "emi_user_id": emi_user.id,
                "user_id": user.id, 
                "plot_id": plot.plot_id,
                "upfront_amount": round(upfront_amount, 2),
                "emi_amount": round(emi_amount, 2),
                "emi_schedule": emi_schedule
            }, status=status.HTTP_200_OK)

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def buy_emi_payment(request):
    selected_plot_id = request.data.get('plot_id')
    months = int(request.data.get('months', 0))

    if months not in [12, 24, 36]:
        return JsonResponse({'error': 'Invalid EMI months. Choose from 12, 24, or 36 months.'}, status=status.HTTP_400_BAD_REQUEST)

    if not selected_plot_id:
        return JsonResponse({'error': 'No plot selected'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        plot = plot_details.objects.get(plot_id=selected_plot_id)
        
    except plot_details.DoesNotExist:
        return JsonResponse({'error': 'failed to purchase plot'}, status= status.HTTP_404_NOT_FOUND)
        
    total_price = plot.price_in_no
    upfront_amount = total_price * 0.5
    emi_amount = round((total_price - upfront_amount) / months, 2)
    
    try:
        order_data = {
            'amount': int(upfront_amount * 100),  
            'currency': 'INR',
            'receipt': f"plot_{plot.plot_id}_emi_purchase_receipt_{int(time_module.time())}"
        }
        order = razorpay_client.order.create(data=order_data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Razorpay order creation failed: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    emi_option, _ = EMIOption.objects.get_or_create(duration_months=months, interest_rate=0)

    plot_purchase = PlotPurchase.objects.create(
        customer=request.user,
        plot=plot,
        payment_type='emi',
        total_amount=total_price,
        down_payment=upfront_amount,
        emi_amount=emi_amount,
        emi_option=emi_option
    )

    
    emi_list = []
    start_date = timezone.now()
    for month in range(1, months + 1):
        temp_date = start_date + relativedelta(months=month)
        due_date = temp_date.replace(day=1, hour=9, minute=0, second=0, microsecond=0)
        emi_list.append(EMIPayment(
            purchase=plot_purchase,
            emi_number=month,
            amount=emi_amount,
            due_date=due_date
        ))

    EMIPayment.objects.bulk_create(emi_list)

    return JsonResponse({
        'success': True,
        'purchase_id': plot_purchase.id,
        'razorpay_order': order,
        'emi_plan': {
            'upfront_amount': upfront_amount,
            'emi_amount': emi_amount,
            'months': months,
            'schedule': [
                {'emi_number': emi.emi_number, 'due_date': emi.due_date, 'amount': emi.amount}
                for emi in emi_list
            ]
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_emi_schedule(request):
    """
    Return EMI schedule with summary:
    - total_amount
    - months_of_emi
    - current_dues
    - reminders (unpaid EMIs)
    - next_due
    - full emi_schedule
    """
    emi_qs = EMIPayment.objects.filter(
        purchase__customer=request.user
    ).select_related("purchase__plot").order_by("due_date")

    if not emi_qs.exists():
        return JsonResponse({'error': 'No EMI records found'}, status=404)

    
    purchase = emi_qs.first().purchase
    total_amount = float(sum(emi.amount for emi in emi_qs))
    months_of_emi = emi_qs.count()

    unpaid_emis = emi_qs.filter(is_paid=False)
    current_dues = unpaid_emis.count()
    next_due = unpaid_emis.order_by("due_date").first()

    emi_schedule = [
        {
            "emi_id": emi.id,
            "plot_id": emi.purchase.plot.plot_id,
            "emi_number": emi.emi_number,
            "amount": float(emi.amount),
            "due_date": emi.due_date,
            "is_paid": emi.is_paid,
            "razorpay_order_id": emi.razorpay_order_id
        }
        for emi in emi_qs
    ]

    reminders = [
        {
            "emi_id": emi.id,
            "emi_number": emi.emi_number,
            "amount": float(emi.amount),
            "due_date": emi.due_date,
        }
        for emi in unpaid_emis
    ]

    result = {
        "plot_id": purchase.plot.plot_id,
        "total_amount": total_amount,
        "months_of_emi": months_of_emi,
        "current_dues": current_dues,
        "reminders": reminders,
        "next_due": {
            "emi_id": next_due.id,
            "emi_number": next_due.emi_number,
            "amount": float(next_due.amount),
            "due_date": next_due.due_date,
        } if next_due else None,
        "emi_schedule": emi_schedule
    }

    return JsonResponse({"success": True, "emi_plan": result}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay_emi_dues(request):
    
    try:
        
        emi = EMIPayment.objects.filter(
            purchase__customer=request.user,
            is_paid=False
        ).order_by("due_date").first()

        if not emi:
            return JsonResponse({'error': 'No pending EMI found'}, status=status.HTTP_404_NOT_FOUND)

      
        if emi.razorpay_order_id:
            return JsonResponse({
                'message': 'Payment already initiated for the next EMI',
                'emi_id': emi.id,
                'amount': float(emi.amount),
                'due_date': emi.due_date,
                'razorpay_order_id': emi.razorpay_order_id
            }, status=status.HTTP_200_OK)

       
        order_data = {
            'amount': int(emi.amount * 100),  
            'currency': 'INR',
            'receipt': f"emi_{emi.id}_payment_receipt_{int(time_module.time())}"
        }

        order = razorpay_client.order.create(data=order_data)

        
        emi.razorpay_order_id = order['id']
        emi.status = "payment_initiated"
        emi.save()

        return JsonResponse({
            'message': 'Next due EMI payment order created',
            'emi_id': emi.id,
            'amount': float(emi.amount),
            'due_date': emi.due_date,
            'razorpay_order': order
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_full_payment(request):
    try:
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_signature = str(request.data.get("razorpay_signature", "").strip())

        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            return JsonResponse({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except SignatureVerificationError:
            return JsonResponse({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        purchase = PlotPurchase.objects.get(
            razorpay_order_id=razorpay_order_id,
            customer=request.user
        )

        if purchase.status == "paid":
            return JsonResponse({
                "success": True,
                "message": "Full payment already verified",
                "plot_purchase_id": purchase.id,
                "status": purchase.status
            }, status=status.HTTP_200_OK)

        
        purchase.status = "paid"
        purchase.payment_id = razorpay_payment_id
        purchase.paid_date = timezone.now()
        purchase.save()

        return JsonResponse({
            "success": True,
            "message": "Full payment verified",
            "plot_purchase_id": purchase.id,
            "status": purchase.status
        }, status=status.HTTP_200_OK)

    except PlotPurchase.DoesNotExist:
        return JsonResponse({'error': 'Purchase record not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_emi_payment(request):
    try:
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = str(request.data.get('razorpay_signature', '').strip())

        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            return JsonResponse({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except SignatureVerificationError:
            return JsonResponse({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        
        emi = EMIPayment.objects.get(
            razorpay_order_id=razorpay_order_id,
            purchase__customer=request.user
        )

    
        if emi.is_paid:
            return JsonResponse({
                'message': 'EMI already marked as paid',
                'emi_id': emi.id,
                'status': emi.status
            }, status=status.HTTP_200_OK)

       
        emi.is_paid = True
        emi.status = 'paid'
        emi.payment_id = razorpay_payment_id
        emi.paid_date = timezone.now()
        emi.save()

        return JsonResponse({
            'message': 'Payment verified successfully',
            'emi_id': emi.id,
            'payment_id': razorpay_payment_id,
            'order_id': razorpay_order_id,
            'status': emi.status
        }, status=status.HTTP_200_OK)

    except EMIPayment.DoesNotExist:
        return JsonResponse({'error': 'EMI payment record not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_plot(request):
    plot_no = request.data.get('plot_no')
    project = request.data.get('project')

    if not plot_no :
        return JsonResponse({'error': 'Plot number is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        plot = plot_details.objects.get(plot_no=plot_no)
    except plot_details.DoesNotExist:
        return JsonResponse({'error': 'Plot not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if plot.status == 'sold':
        return JsonResponse({'error': 'Plot is already sold'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    plot.status = 'sold'
    plot.buyer = request.user
    plot.save()

    return JsonResponse({'message': f'Plot {plot_no} purchased successfully by {request.user.username}'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def properties_view(request):
    id = request.user.id
    print(id)
    buyplots = PlotPurchase.objects.filter(customer=id)
    propertiesview = []
    for buyplot in buyplots:
        print(buyplot.plot_id)
        plotdetails = plot_details.objects.get(plot_id = buyplot.plot_id)
        propertiesview.append({"plot_id":plotdetails.plot_id, "plot_no":plotdetails.plot_no,
                               "sqft_area":plotdetails.sqft_area, "facing":plotdetails.facing,
                               "price_in_no":plotdetails.price_in_no, "price_in_words":plotdetails.price_in_words,
                               "project":plotdetails.project, "city":plotdetails.city,
                               "owner":request.user.full_name, "ipfs_url":buyplot.ipfs_url, "email":request.user.email, "phone_number":request.user.phone_number,
                               "address":request.user.address, "purchase_date":buyplot.purchase_date, "payment_type":buyplot.payment_type,
                               })

    return JsonResponse({"data": list(propertiesview)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    id = request.user.id
    print(id)
    buyplots = PlotPurchase.objects.filter(customer=id)
    Transaction_History = []
    for transaction in buyplots:
        print(transaction.id)
        if Payment.objects.filter(purchase = transaction.id):
            payment_detail = Payment.objects.get(purchase = transaction.id)
            Transaction_History.append({'amount':payment_detail.amount, 'payment_date':payment_detail.payment_date, 'payment_type':transaction.payment_type})
        
        if EMIPayment.objects.filter(purchase = transaction.id):
            emipayment_detail = EMIPayment.objects.get(purchase = transaction.id)
            Transaction_History.append({'amount':emipayment_detail.amount, 'payment_date':emipayment_detail.paid_date, 'payment_type':transaction.payment_type, 'eminumber':emipayment_detail.emi_number})
    return JsonResponse({"data": list(Transaction_History)})

	 

