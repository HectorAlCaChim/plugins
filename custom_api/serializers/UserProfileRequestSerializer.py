from rest_framework import serializers
class UserProfileRequestSerializer(
    serializers.Serializer
):

    name = serializers.CharField(
        required=True
    )