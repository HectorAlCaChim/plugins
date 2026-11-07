from rest_framework import serializers

class BulkUserStatusItemSerializer(
    serializers.Serializer
):

    userId = serializers.IntegerField()

    isActive = serializers.BooleanField()


class BulkUserStatusRequestSerializer(
    serializers.Serializer
):

    users = BulkUserStatusItemSerializer(
        many=True
    )