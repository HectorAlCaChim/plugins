from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from custom_api.serializers.WorkshopCompletionUserSerializer import (
    WorkshopCompletionRequestSerializer,
    WorkshopCompletionUserSerializer
)

from custom_api.services.workshop_completion_service import (
    WorkshopCompletionService
)
class WorkshopCompletionView(APIView):

    def post(self, request):

        serializer = (
            WorkshopCompletionRequestSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        service = (
            WorkshopCompletionService()
        )

        result = (
            service.get_workshop_completion_status(
                serializer.validated_data["users"],
                serializer.validated_data["passingGrade"]
            )
        )

        return Response(
            result,
            status=status.HTTP_200_OK
        )