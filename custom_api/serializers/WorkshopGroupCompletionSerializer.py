from rest_framework import serializers


class WorkshopCompletionGroupBulkUserSerializer(
    serializers.Serializer
):
    referenceId = serializers.CharField(
        required=True
    )

    openEdxUserId = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    email = serializers.EmailField(
        required=True
    )

    workshopNames = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False
    )


class WorkshopCompletionGroupBulkRequestSerializer(
    serializers.Serializer
):
    passingGrade = serializers.IntegerField()

    users = WorkshopCompletionGroupBulkUserSerializer(
        many=True
    )