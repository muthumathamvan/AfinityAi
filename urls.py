from django.urls import path
from django.contrib.auth import views as auth_views
from . import api_views, blockchain, admin_views

urlpatterns = [
    path('cities/', api_views.get_all_cities, name='search_cities'),
    path('projects/', api_views.get_projects_by_city, name='get_projects_by_city'),
    path('plots/', api_views.get_plots_by_project, name='get_plots_by_project'),
    path('select-plot/', api_views.select_plot, name='select_plot'),
    path('get-plot/', api_views.get_selected_plot_after_login, name='get_selected_plot_after_login'),
    path('buy-plot/', api_views.buy_plot, name='buy_plot'),
    path('status/', api_views.check_reserved_plot, name='check_reserved_plots'),
    # Authentication URLs
    path('register/', api_views.register_user, name='register'),
    path('login/',api_views.login_user, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('user-dashboard/', api_views.user_dashboard, name='user_dashboard'),
    path('plot-full-purchase/', api_views.buy_plot_full, name='buy_plot_full'),
    path('buy-in-emi/', api_views.buy_emi_payment, name='buy_plot_emi'),
    path('emi-options/', api_views.get_emi_options, name='get_emi_options'), 
    path('emi-plans/', api_views.emi_plans, name='emi_plans'),
    path('emi/save-user-info/', api_views.save_emi_user_info, name="save_emi_user_info"),
    path('verify-payment/', api_views.verify_full_payment, name='verify_full_payment_razorpay'),
    path('emi/schedule/', api_views.get_emi_schedule, name='get_emi_schedule'),
    path('emi/pay-due/', api_views.pay_emi_dues, name='pay_emi_dues'), 
    path('emi/verify-emi-payment/', api_views.verify_emi_payment, name='verify_emi_payment_razorpay'),
    # transaction history
    path('transaction-history/', api_views.transaction_history, name='transaction_history'),

    # KYC and Documents
    #path('kyc/upload/', views.kyc_upload, name='kyc_upload'),
    
    # EMI Calculator
    # path('emi-calculator/', views.emi_calculator, name='emi_calculator'),
    path('full-payment/', blockchain.full_Payment, name='emi_calculator'),
    path('properties_view/', api_views.properties_view, name="properties_view"),

    # admin_views.py
    path('admin-emi-options/', admin_views.emi_options, name="_emi_options"),

    path('admin-emi-options/<int:option_id>/', admin_views.emi_options, name="emi_options"),

]