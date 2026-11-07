from rest_framework import serializers
class UpdateUserRequestSerializer(
    serializers.Serializer
):

    userName = serializers.CharField(
        required=False
    )

    password = serializers.CharField(
        required=False
    )

    firstName = serializers.CharField(
        required=False
    )

    lastName = serializers.CharField(
        required=False
    )

    email = serializers.EmailField(
        required=False
    )

    isSuperuser = serializers.BooleanField(
        required=False
    )

    isStaff = serializers.BooleanField(
        required=False
    )

    isActive = serializers.BooleanField(
        required=False
    )