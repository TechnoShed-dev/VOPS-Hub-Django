# VOPS-Hub/core_app/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse

def group_required(group_names, redirect_url='core_app:vessel_list'):
    """
    Decorator for views that checks if the user is in a specific group.
    If not in the group, redirects to a specified URL (defaulting to vessel_list).
    `group_names` can be a single string or a list/tuple of strings.
    """
    if not isinstance(group_names, (list, tuple)):
        group_names = [group_names]

    def check_group(user):
        if user.is_authenticated:
            # Check if the user is a superuser (superusers bypass group checks)
            if user.is_superuser:
                return True
            # Check if the user belongs to any of the required groups
            return user.groups.filter(name__in=group_names).exists()
        return False # Not authenticated

    # Redirect unauthenticated users to login, unauthorized authenticated users to redirect_url
    def decorator(view_func):
        decorated_view = user_passes_test(check_group, login_url='admin:login', redirect_field_name=None)(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not check_group(request.user) and request.user.is_authenticated:
                return redirect(reverse(redirect_url))
            return decorated_view(request, *args, **kwargs)
        return _wrapped_view
    return decorator