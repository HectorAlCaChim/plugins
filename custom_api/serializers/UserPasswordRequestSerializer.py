from rest_framework import serializers
class UserPasswordRequestSerializer(
    serializers.Serializer
):

    password = serializers.CharField(
        required=True
    )