from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from edx_rest_framework_extensions.auth.jwt.authentication import (
    JwtAuthentication
)

from custom_api.services.enrollment_service import (
    EnrollmentService
)


class BulkCourseEnrollmentAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        result = (
            EnrollmentService.bulk_course_enrollment(
                username=request.data.get(
                    "user"
                ),
                action=request.data.get(
                    "action"
                ),
                course_ids=request.data.get(
                    "courseIds"
                )
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
            {
                "success": True,
                **result["data"]
            },
            status=200
        )

class BulkUsersCourseEnrollmentAPIView(APIView):

    authentication_classes = [
        OAuth2Authentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request
    ):

        result = (
            EnrollmentService
            .bulk_users_course_enrollment(
                request.data.get("users")
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
            {
                "success": True,
                **result["data"]
            },
            status=200
        )

class BulkUsersSharedCoursesAPIView(APIView):

    authentication_classes = [
        OAuth2Authentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request
    ):

        result = (
            EnrollmentService.bulk_by_users(
                users=request.data.get(
                    "users"
                ),
                action=request.data.get(
                    "action"
                ),
                course_ids=request.data.get(
                    "courseIds"
                )
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
