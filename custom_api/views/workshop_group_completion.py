from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication
)

from custom_api.serializers.WorkshopGroupCompletionSerializer import (
    WorkshopCompletionGroupBulkRequestSerializer
)

from custom_api.services.workshop_group_completion_service import (
    WorkshopCompletionGroupBulkService
)


class WorkshopCompletionGroupBulkAPIView(
    APIView
):
    authentication_classes = [
        OAuth2Authentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = (
            WorkshopCompletionGroupBulkRequestSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = (
            WorkshopCompletionGroupBulkService
                .get_completion_status(
                    users=serializer.validated_data["users"],
                    passing_grade=serializer.validated_data["passingGrade"]
                )
        )

        return Response(
            result,
            status=status.HTTP_200_OK
        )