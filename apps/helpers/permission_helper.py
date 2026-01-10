import time
import hmac
import hashlib
from rest_framework.permissions import BasePermission
from app import settings
from rest_framework.exceptions import APIException
from django.shortcuts import redirect
from django.http import JsonResponse

class AccessDeniedException(APIException):
    status_code = 403
    default_detail = 'Access Denied. Required headers missing or invalid.'
    default_code = 'access_denied'

class HasValidAppSignature(BasePermission):
    def has_permission(self, request, view):
        app_id = request.headers.get('X-APP-ID')
        timestamp = request.headers.get('X-APP-TIMESTAMP')
        nonce = request.headers.get('X-APP-NONCE')
        signature = request.headers.get('X-APP-SIGNATURE')
        
        # Check all required headers
        if not all([app_id, timestamp, nonce, signature]):
            raise AccessDeniedException()

        secret = settings.APP_SECRETS.get(app_id)
        if not secret:
            raise AccessDeniedException()

        try:
            timestamp = int(timestamp)
        except ValueError:
            raise AccessDeniedException()

        # Validate time window (within 5 minutes)
        current_time = int(time.time())
        if abs(current_time - timestamp) > 300:
            raise AccessDeniedException()

        # Recalculate signature
        message = f"{app_id}{timestamp}{nonce}".encode()
        expected_signature = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

def custom_exception_handler(exc, context):
    request = context.get("request")

    if isinstance(exc, AccessDeniedException):
        accept = request.headers.get("Accept", "")
        user_agent = request.headers.get("User-Agent", "")

        # If the request prefers HTML or is a browser
        if "text/html" in accept or "Mozilla" in user_agent:
            return redirect('/access-denied/')
        
        # Otherwise, assume it's an API client like Postman
        return JsonResponse({"detail": str(exc)}, status=403)
