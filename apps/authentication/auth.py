import jwt
import json
import hashlib
import datetime
from app import settings
from rest_framework import status
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.views import APIView
from django.db import transaction, IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.helpers.general_helper import *
from apps.models import BlacklistedToken, Users

import logging
logger = logging.getLogger(__name__)


class OwnerSignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        response_data = {'status': False,'message': ''}

        email = request.data.get('email')
        mobile_number = request.data.get('mobile_number')
        mobile_number = str(mobile_number).strip()

        if not email or not mobile_number:
            response_data['message'] = 'Email and Mobile Number are required.'
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_message = validate_mobile_number(mobile_number)
        if not is_valid:
            response_data["message"] = error_message
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        is_valid, error_message = validate_email_address(email)
        if not is_valid:
            response_data["message"] = error_message
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        username = request.data.get('username')
        if not username:
            response_data['message'] = 'Username is required.'
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        username = str(username).strip()
        if Users.objects.filter(username=username).exists():
            response_data['message'] = 'Username already exists.'
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get('password')
        is_valid, error_message = validate_password(password=password, email=email)
        if not is_valid:
            response_data["message"] = error_message
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = hashlib.md5(password.encode()).hexdigest()

        # -----------------------------------------------------
        # Creating User Account
        # -----------------------------------------------------
        try:
            with transaction.atomic():
                user = Users.objects.create(
                    username=username,
                    password=hashed_password,
                    mobile_number=mobile_number,
                    email=email,
                    role='OWNER',
                    is_active=True
                )
                user.save()

            response_data['status'] = True
            response_data['message'] = 'Store Owner account created successfully.'
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            response_data['message'] = 'User with this email or mobile number already exists.'
            response_data['error'] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            response_data['message'] = 'An error occurred while creating the user.'
            response_data['error'] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def generate_user_token(user, expiration_minutes=None, expiration_days=None, token_type='access'):
    """Generate JWT token for authenticated user"""

    if not expiration_minutes and not expiration_days:
        raise ValueError("Either expiration_minutes or expiration_days must be provided")

    expiration = datetime.datetime.utcnow() + (
        datetime.timedelta(minutes=expiration_minutes)
        if expiration_minutes
        else datetime.timedelta(days=expiration_days)
    )

    payload = {
        'user_id': user.id,
        'full_name': user.full_name,
        'username': user.username,
        'email': user.email,
        'mobile_number': user.mobile_number,
        'role_name': user.role_name,
        'type': token_type,
        'exp': expiration,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


class LoginView(APIView):

    def post(self, request):
        response_data = {'status': False, 'message': ''}

        username = request.data.get('username')
        email = request.data.get('email')
        mobile = request.data.get('mobile_number')
        password = request.data.get('password')

        #Validator: At least one identifier required
        if not any([username, email, mobile]):
            response_data['message'] = 'Username or Email or Mobile number is required.'
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            response_data['message'] = 'Password is required.'
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        #Fetch user
        user_object = None
        if username:
            user_object = Users.objects.filter(username=username).first()
        elif email:
            user_object = Users.objects.filter(email=email).first()
        elif mobile:
            user_object = Users.objects.filter(mobile_number=mobile).first()

        if not user_object:
            response_data['message'] = 'Invalid credentials.'
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        #Password check
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        if user_object.password != hashed_password:
            response_data['message'] = 'Incorrect password.'
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        #Token generation
        access_token = generate_user_token(
            user=user_object,
            expiration_days=1,
            token_type='access'
        )

        refresh_token = generate_user_token(
            user=user_object,
            expiration_days=90,
            token_type='refresh'
        )

        response_data.update({
            'status': True,
            'message': 'Login successful.',
            'access_token': access_token,
            'refresh_token': refresh_token,
        })

        return JsonResponse(response_data, status=status.HTTP_200_OK)

class GenerateAccessToken(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        response_data = {
            'status': False,
            'message': '',
            'access_token': None,
            'error': None
        }

        body = request.data
        refresh_token = body.get('refresh_token')

        if not refresh_token:
            response_data['message'] = 'Refresh token is required.'
            response_data['error'] = 'No refresh_token provided.'
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Check if refresh token is blacklisted
        if BlacklistedToken.objects.filter(token=refresh_token).exists():
            response_data['message'] = 'Refresh token is invalid or has been blacklisted.'
            return JsonResponse(response_data, status=status.HTTP_401_UNAUTHORIZED)

        # Decode and verify refresh token
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            response_data['message'] = 'Refresh token has expired. Please log in again.'
            return JsonResponse(response_data, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            response_data['message'] = 'Invalid refresh token.'
            return JsonResponse(response_data, status=status.HTTP_401_UNAUTHORIZED)

        # Verify token type
        if payload.get('type') != 'refresh':
            response_data['message'] = 'Invalid token type.'
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        user_id = payload.get('user_id')
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            response_data['message'] = 'User not found.'
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        access_token = generate_user_token(
            user,
            expiration_days=1,
            token_type='access'
        )

        response_data['status'] = True
        response_data['message'] = 'Access token refreshed successfully.'
        response_data['access_token'] = access_token
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response_data = {
            'status': False,
            'message': '',
            'error': None,
            'data': None
        }
        
        try:
            body = json.loads(request.body)
            refresh_token = body.get('refresh_token')
            access_token = body.get('access_token')
            user = request.user

            if not refresh_token or not access_token:
                response_data['message'] = "Both refresh and access tokens are required in the request body."
                response_data  ['error'] = "Tokens are not provided."
                return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
                

            # Decode and validate the tokens
            self._decode_token(refresh_token, token_type='refresh')
            self._decode_token(access_token, token_type='access')

            # Blacklist the tokens
            self._blacklist_tokens([refresh_token, access_token])

            # Dynamically determine identifier (email or mobile)
            identifier = user.email or user.mobile_number
            cache.delete(f"user_token_data:{identifier}")

            # Optionally clear session if you use it
            request.session.flush()

            response_data['status'] = True
            response_data['message'] = "Logout Successfully."
            return JsonResponse(response_data, status = status.HTTP_200_OK)


        except json.JSONDecodeError:
            response_data['message'] = "Invalid JSON in request body."
            response_data['error'] = "Json Decode Error"
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            response_data['message'] = "Invalid JSON in request body."
            response_data['error'] = f'An error occurred: {str(e)}'
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
            
    def _decode_token(self, token, token_type):
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            pass
        except jwt.DecodeError:
            raise ValueError(f'Invalid {token_type} token.')

    def _blacklist_tokens(self, tokens):
        for token in tokens:
            if not BlacklistedToken.objects.filter(token=token).exists():
                BlacklistedToken.objects.create(token=token)
