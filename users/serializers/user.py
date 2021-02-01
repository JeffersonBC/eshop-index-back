
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

from rest_framework import serializers


# Validator functions
def username_exists(value):
    if get_user_model().objects.filter(username=value).count() > 0:
        raise serializers.ValidationError("Username already exists.")


def email_exists(value):
    if get_user_model().objects.filter(email=value).count() > 0:
        raise serializers.ValidationError(
            "Email address already associated with an account.")

def password_valid(value):
    try:
        password_validation.validate_password(value)
    except ValidationError as e:
        errorString = ''

        errorsLen = len(e.error_list)
        for i in range(errorsLen):
            errorString += e.error_list[i].message
            if (i + 1) < errorsLen:
                errorString += '<br>'

        raise serializers.ValidationError(errorString)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[username_exists])
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(validators=[email_exists])
    password = serializers.CharField(validators=[password_valid])

    is_active = serializers.BooleanField(default=False)
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)

    def create(self, validated_data):
        user = get_user_model().objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            is_active=False,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate(self, data):
        return data

    class Meta:
        model = get_user_model()
        write_only_fields = ['password']
        read_only_fields = ['id']
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'is_active',
            'is_staff',
            'is_superuser'
        )
