import jwt
import datetime
from app import settings

def generate_user_token(request, user, role_name, full_name, 
                       expiration_minutes=None, expiration_days=None, 
                       token_type='access'):
    """Generate JWT token for authenticated user"""
    expiration = datetime.datetime.utcnow() + (
        datetime.timedelta(minutes=expiration_minutes) if expiration_minutes 
        else datetime.timedelta(days=expiration_days)
    )
    
    # Build full image URL if image_url is present
    image_url = getattr(user, 'image_url', '')
    if image_url:
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        full_image_url = f"{scheme}://{host}/getImage?file={image_url}"
    else:
        full_image_url = ''

    base_payload = build_default_payload(user, role_name, full_name, token_type, expiration, full_image_url)

    role_payload_adders = {
        3: add_seller_payload_fields,
        # Add future role handlers here
    }

    adder = role_payload_adders.get(user.role_id)
    if adder:
        base_payload.update(adder(user))

    return jwt.encode(base_payload, settings.SECRET_KEY, algorithm='HS256')


def build_default_payload(user, role_name, full_name, token_type, expiration, full_image_url):
    return {
        'user_id': user.id,
        'provider_id': user.provider_id,
        'role_id': user.role_id,
        'role_name': role_name,
        'full_name': full_name,
        'image_url': full_image_url,
        'type': token_type,
        'exp': expiration,
    }

def add_seller_payload_fields(user):
    return {
        'is_profile_completed': user.is_profile_completed,
        'profile_completion_percentage': getattr(user, 'profile_completion_percentage', 0),
    }