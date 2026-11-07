from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from edx_rest_framework_extensions.auth.jwt.authentication import (
    JwtAuthentication
)

from custom_api.services.instructor_service import (
    InstructorService
)


class InstructorSearchAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if not request.user.is_staff:

            return Response(
                {
                    "success": False,
                    "message": "Permission denied"
                },
                status=403
            )

        course_ids = request.data.get(
            "courseIds",
            []
        )

        result = InstructorService.get_instructors(
            course_ids
        )

        if not result["success"]:

            return Response(
                {
                    "success": False,
                    "message": result["message"]
                },
                status=result["status"]
            )

        return Response(
            result["data"],
            status=200
        )