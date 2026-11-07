from rest_framework import serializers
class UserStatusRequestSerializer(
    serializers.Serializer
):

    isActive = serializers.BooleanField(
        required=True
    )