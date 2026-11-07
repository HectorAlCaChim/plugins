from rest_framework import serializers


class CreateUserRequestSerializer(
    serializers.Serializer
):

    userName = serializers.CharField(
        required=True
    )

    password = serializers.CharField(
        required=False
    )

    firstName = serializers.CharField(
        required=True
    )

    lastName = serializers.CharField(
        required=True
    )

    email = serializers.EmailField(
        required=True
    )

    isSuperuser = serializers.BooleanField(
        required=False,
        default=False
    )

    isStaff = serializers.BooleanField(
        required=False,
        default=False
    )

    isActive = serializers.BooleanField(
        required=False,
        default=True
    )