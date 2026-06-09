from .models import AuditLog


def log_action(request_or_user, action, module, description='', extra_data=None):
    """
    Call this from any view to record an action.
    Pass either a DRF request (has .user) or a User instance directly.
    """
    if hasattr(request_or_user, 'user'):
        user       = request_or_user.user
        ip_address = _get_ip(request_or_user)
    else:
        user       = request_or_user
        ip_address = ''

    AuditLog(
        user_email  = getattr(user, 'email', 'anonymous'),
        user_role   = getattr(user, 'role', 'unknown'),
        action      = action,
        module      = module,
        description = description,
        ip_address  = ip_address,
        extra_data  = extra_data or {},
    ).save()


def _get_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')