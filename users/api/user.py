import requests


from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from eshop_crawler.settings import RECAPTCHA_SECRET_KEY

from users.emails import AccountActivationEmail, AccountPasswordResetEmail
from users.models import Following
from users.serializers.user import UserSerializer
from users.serializers.user_profile import user_to_profile_json


@api_view(['GET'])
def current_user(request):
    if not request.auth:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    return Response(
        UserSerializer(request.user).data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def user_create(request):
    # If user hasn't sent captcha response, or if it's invalid, respond '400'
    captcha = request.data['captcha']
    if not captcha:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        catpcha_data = {'secret': RECAPTCHA_SECRET_KEY, 'response': captcha}
        req = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=catpcha_data)

        if req.status_code != 200:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    serialized = UserSerializer(data=request.data)
    if serialized.is_valid():
        user = serialized.save()

        email = AccountActivationEmail()
        context = {
            'url': settings.WEBSITE_URL,
            'user_id_b64': urlsafe_base64_encode(force_bytes(user.id))
                           .decode(),
            'token': default_token_generator.make_token(user),
        }

        email.send(user.email, context,
                   from_email=settings.EMAIL_HOST_USER)

        return Response(status=status.HTTP_201_CREATED)

    else:
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_activate(request, user_id_b64, token):
    user_id = urlsafe_base64_decode(user_id_b64)
    user = get_object_or_404(get_user_model(), id=user_id)

    if default_token_generator.check_token(user, token):
        try:
            user.is_active = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def user_resend_activation_email(request):
    # If user hasn't sent captcha response, or if it's invalid, respond '400'
    captcha = request.data['captcha']
    if not captcha:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        catpcha_data = {'secret': RECAPTCHA_SECRET_KEY, 'response': captcha}
        req = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=catpcha_data)

        if req.status_code != 200:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(get_user_model(), email=request.data['email'])

    if user.is_active:
        return Response(status=status.HTTP_404_NOT_FOUND)

    email = AccountActivationEmail()
    context = {
        'url': settings.WEBSITE_URL,
        'user_id_b64': urlsafe_base64_encode(force_bytes(user.id))
                       .decode(),
        'token': default_token_generator.make_token(user),
    }

    email.send(user.email, context,
               from_email=settings.EMAIL_HOST_USER)

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def user_send_password_reset_email(request):
    # If user hasn't sent captcha response, or if it's invalid, respond '400'
    captcha = request.data['captcha']
    if not captcha:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        catpcha_data = {'secret': RECAPTCHA_SECRET_KEY, 'response': captcha}
        req = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=catpcha_data)

        if req.status_code != 200:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    user_email = request.data['email']

    if not user_email:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(get_user_model(), email=user_email)

    email = AccountPasswordResetEmail()
    context = {
        'url': settings.WEBSITE_URL,
        'user_id_b64': urlsafe_base64_encode(force_bytes(user.id))
                       .decode(),
        'user_first_name': user.first_name,
        'token': default_token_generator.make_token(user),
    }

    email.send(user.email, context, from_email=settings.EMAIL_HOST_USER)

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def user_password_reset(request, user_id_b64, token):
    user_id = urlsafe_base64_decode(user_id_b64)
    user = get_object_or_404(get_user_model(), id=user_id)

    new_password = request.data['password']
    if not new_password:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    errorString = ''
    try:
        password_validation.validate_password(new_password)
    except ValidationError as e:
        errorsLen = len(e.error_list)
        for i in range(errorsLen):
            errorString += e.error_list[i].message
            if (i + 1) < errorsLen:
                errorString += '<br>'

    if errorString:
        return Response(
            {'password': errorString},
            status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        try:
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def verify_token(request):
    return Response(True, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def verify_admin(request):
    return Response(True, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_profile_by_username(request, username):
    user = get_object_or_404(get_user_model(), username=username)

    return Response(
        user_to_profile_json(user, request),
        status=status.HTTP_200_OK)
