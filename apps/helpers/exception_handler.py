from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, NotAuthenticated
from rest_framework.views import exception_handler as drf_default_exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from django.http import JsonResponse
from apps.helpers.permission_helper import AccessDeniedException


def custom_exception_handler(exc, context):
    request = context.get("request")

    if isinstance(exc, AccessDeniedException):
        accept = request.headers.get("Accept", "")
        user_agent = request.headers.get("User-Agent", "")

        if "text/html" in accept or "Mozilla" in user_agent:
            return redirect('/access-denied/')
        
        return JsonResponse({"detail": str(exc)}, status=403)

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return Response({
            "status": False,
            "message": str(exc)
        }, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, PermissionDenied):
        return Response({
            "status": False,
            "message": str(exc)
        }, status=status.HTTP_403_FORBIDDEN)
    
    response = drf_default_exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict):
        detail = response.data.get('detail', 'Something went wrong')
        response.data.clear()
        response.data['status'] = False
        response.data['message'] = detail

    return response
