import jwt
from django.conf import settings
from apps.models import Users, BlacklistedToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication

class CustomUserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        if BlacklistedToken.objects.filter(token=token).exists():
            raise AuthenticationFailed('Token is invalid or has been blacklisted. Please log in again.')

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')

            if not user_id:
                raise AuthenticationFailed('Invalid token: User information missing.')

            try:
                user = Users.objects.get(id=user_id) #Self Seller Verification
                user.is_authenticated = True  # Dynamically add the attribute
                return (user, None)
            except Users.DoesNotExist:
                raise AuthenticationFailed('User not found.')
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired. Please log in again.')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token. Please log in again.')


