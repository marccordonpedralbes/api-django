"""Users serializers."""

# Django
from ccy.core.currency import currency
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator, validate_email
from django.shortcuts import get_object_or_404
from django.db.models import Sum

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Models
from api.users.models import User, UserLoginActivity
from djmoney.models.fields import Money


# Serializers

# Celery
from api.taskapp.tasks import (
    send_confirmation_email,
    send_change_email_email,
    send_reset_password_email,
    send_invitation_email
)


# Utilities
import jwt
import datetime
from django.utils import timezone

from api.utils import helpers
import re
import geoip2.database
import ccy

import environ
env = environ.Env()


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'about',
            'phone_number',
            'country',
            'is_staff',
            'is_verified',
            'picture',
        )




class GetUserByJwtSerializer(serializers.Serializer):
    user = UserModelSerializer(read_only=True)
    access_token = serializers.CharField(read_only=True)
    token = serializers.CharField()

    def validate_token(self, data):
        """Verifiy token is valid."""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY,
                                 algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'user_token':
            raise serializers.ValidationError('Invalid token')

        self.context['payload'] = payload

        return data

    def validate(self, data):
        payload = self.context['payload']
        user = User.objects.get(id=payload['user'])
        token, created = Token.objects.get_or_create(
            user=user)
        data['access_token'] = token
        data['user'] = user
        return data


class UserSignUpSerializer(serializers.Serializer):
    """Useer sign up serializer.

    Handle sign up data validation and user/profile creation.
    """

    email = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=False,
    )
    username = serializers.CharField(
        min_length=4,
        max_length=40,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    # Phone number
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: +999999999. Up to 15 digits allowed."
    )
    phone_number = serializers.CharField(
        validators=[phone_regex], required=False)

    # Password
    password = serializers.CharField(min_length=8, max_length=64)
    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    # Name
    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)


    def validate(self, data):
        """Verify passwords match."""
        passwd = data['password']
        passwd_conf = data['password_confirmation']
        if passwd != passwd_conf:
            raise serializers.ValidationError('Las contraseñas no coinciden')
        password_validation.validate_password(passwd)


        return data

    def create(self, data):
        """Handle user and profile creation."""
        request = self.context['request']

        data.pop('password_confirmation')

        # Create the free trial expiration date


     
        expiration_date = timezone.now() + datetime.timedelta(days=14)
        user = User.objects.create_user(**data,
                                        is_verified=False,
                                        is_client=True,
 
                                    )

        token, created = Token.objects.get_or_create(
            user=user)

        current_login_ip = helpers.get_client_ip(request)

        if UserLoginActivity.objects.filter(user=user).exists():
            user_login_activity = UserLoginActivity.objects.filter(
                user=user)[0]
            if user_login_activity.login_IP != current_login_ip:
                if Token.objects.filter(user=user).exists():
                    last_token = Token.objects.get(user=user)
                    last_token.delete()
            UserLoginActivity.objects.filter(
                login_username=user.username).delete()

        user_agent_info = request.META.get(
            'HTTP_USER_AGENT', '<unknown>')[:255],
        user_login_activity_log = UserLoginActivity(login_IP=helpers.get_client_ip(request),
                                                    user=user,
                                                    login_username=user.username,
                                                    user_agent_info=user_agent_info,
                                                    status=UserLoginActivity.SUCCESS)
        user_login_activity_log.save()

        send_confirmation_email(user)

        return user, token.key


class UserLoginSerializer(serializers.Serializer):
    """User login serializer.

    Handle the login request
    """

    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """Check credentials."""
        # Validation with email or password

        email = data['email']
        password = data['password']
        request = self.context['request']
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        # for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if email and password:
            if re.search(regex, email):
                user_request = get_object_or_404(
                    User,
                    email=email
                )
                email = user_request.username
            # Check if user set email

        users = User.objects.filter(username=email, account_deactivated=True)

        if users.exists():
            raise serializers.ValidationError(
                'This account has already been desactivated')

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError(
                'Invalid credentials')

        if user:
            current_login_ip = helpers.get_client_ip(request)

            if UserLoginActivity.objects.filter(user=user).exists():
                user_login_activity = UserLoginActivity.objects.filter(
                    user=user)[0]
                if user_login_activity.login_IP != current_login_ip:
                    if Token.objects.filter(user=user).exists():
                        last_token = Token.objects.get(user=user)
                        last_token.delete()
                UserLoginActivity.objects.filter(
                    user=user).delete()
            user_agent_info = request.META.get(
                'HTTP_USER_AGENT', '<unknown>')[:255],
            user_login_activity_log = UserLoginActivity(login_IP=helpers.get_client_ip(request),
                                                        user=user,
                                                        login_username=user.username,
                                                        user_agent_info=user_agent_info,
                                                        status=UserLoginActivity.SUCCESS)
            user_login_activity_log.save()

        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retrieve new token."""

        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key


class AccountVerificationSerializer(serializers.Serializer):
    """Acount verification serializer."""

    token = serializers.CharField()

    def validate_token(self, data):
        """Verifiy token is valid."""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY,
                                 algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token')
        self.context['payload'] = payload
        return data

    def save(self):
        """Update user's verified status."""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        if user.is_verified:
            raise serializers.ValidationError('Your account is already validated')

        user.is_verified = True
        user.save()


class IsEmailAvailableSerializer(serializers.Serializer):
    """Acount verification serializer."""

    email = serializers.CharField()

    def validate(self, data):
        """Update user's verified status."""

        email = data['email']

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already in use')

        return {"email": email}


class IsCouponAvailableSerializer(serializers.Serializer):
    """Acount verification serializer."""

    coupon = serializers.CharField()

    def validate(self, data):
        """Update user's verified status."""

        coupon = data['coupon']
        stripe = self.context['stripe']
        try:
            stripe_coupon = stripe.Coupon.retrieve(coupon)
            if not stripe_coupon['valid']:
                raise serializers.ValidationError('This coupon is not valid')

        except:
            raise serializers.ValidationError('This coupon does not exist')

        return {"coupon": coupon}


class IsUsernameAvailableSerializer(serializers.Serializer):
    """Acount verification serializer."""

    username = serializers.CharField()

    def validate(self, data):
        """Update user's verified status."""

        username = data['username']

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('This username is already in use')

        return True


class ChangeEmailSerializer(serializers.Serializer):
    """Acount verification serializer."""

    email = serializers.CharField()

    def validate(self, data):
        """Update user's verified status."""

        email = data['email']
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already in use')

        user = self.context['user']

        send_change_email_email(user, email)
        return {'email': email, 'user': user}


class ValidateChangeEmail(serializers.Serializer):
    """Acount verification serializer."""

    token = serializers.CharField()

    def validate_token(self, data):
        """Verifiy token is valid."""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY,
                                 algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'change_email':
            raise serializers.ValidationError('Invalid token')
        self.context['payload'] = payload
        return data

    def save(self):
        """Update user's verified status."""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        email = payload['email']

        user.email = email
        user.save()
        return email


class ForgetPasswordSerializer(serializers.Serializer):
    """Acount verification serializer."""

    email = serializers.CharField()

    def validate(self, data):
        """Update user's verified status."""

        email = data['email']

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email does not exists')

        send_reset_password_email(email)
        return {'email': email}


class ResetPasswordSerializer(serializers.Serializer):
    """Acount verification serializer."""

    token = serializers.CharField()
    password = serializers.CharField(min_length=8, max_length=64)
    confirm_password = serializers.CharField(min_length=8, max_length=64)

    def validate_token(self, data):
        """Verifiy token is valid."""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY,
                                 algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token')
        self.context['payload'] = payload
        return data

    def validate(self, data):

        password = data['password']
        confirm_password = data['confirm_password']
        if password != confirm_password:
            raise serializers.ValidationError('Passwords don\'t match')
        return data

    def save(self):
        """Update user's verified status."""
        username = self.context['payload']['user']

        password = self.data['password']
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """User login serializer.

    Handle the login request
    """
    password = serializers.CharField(min_length=8, max_length=64)
    new_password = serializers.CharField(min_length=8, max_length=64)
    repeat_password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """Check credentials."""
        # Validation with email or password
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        # for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        user = self.context['request'].user
        password = data['password']
        email = user.email
        if email and password:
            if re.search(regex, email):
                user_request = get_object_or_404(
                    User,
                    email=email
                )
                email = user_request.username
            # Check if user set email

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Current password is not correct')
        new_password = data['new_password']
        repeat_password = data['repeat_password']
        if new_password != repeat_password:
            raise serializers.ValidationError('Passwords not match')
        user.set_password(new_password)
        user.password_changed = True
        user.save()

        return data


