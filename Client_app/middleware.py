from django.shortcuts import redirect
from django.urls import resolve

class RoleBasedAccessMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

        # Define role based URL access
        self.role_permissions = {
            # 'superadmin': ['home', 'call_history', 'widget_calls', 'hubspot_config','ai_form', 'logout'],
            'admin': ['home', 'call_history', 'widget_calls', 'logout', 'logout', "client", "branch", "create_branch", "assistant", "create_user", "outbound_call", "widget_calls_loc", "ai_form", "inboundcall", "inboundcall_loc", "create_ai", "loader_page", "assistant_list", "widgetconfiguration", "widget_configuration"],
            'user': ['home', 'call_history', 'widget_calls', 'logout', 'logout'],
        }

    def __call__(self, request):

        if request.user.is_authenticated:

            # ✅ Allow superadmin full access
            if request.user.role == "superadmin":
                return self.get_response(request)

            current_url = resolve(request.path_info).url_name
            allowed_urls = self.role_permissions.get(request.user.role, [])

            if current_url and current_url not in allowed_urls:
                return redirect('home')

        return self.get_response(request)
