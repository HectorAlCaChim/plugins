from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from edx_rest_framework_extensions.auth.jwt.authentication import (
    JwtAuthentication
)

from custom_api.services.grade_service import (
    GradeService
)


class StudentGradesAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]


    def post(self, request):

        result = GradeService.get_student_grades(
            open_edx_user_id=request.data.get(
                "openEdxUserId"
            ),
            course_ids=request.data.get(
                "courseIds"
            )
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