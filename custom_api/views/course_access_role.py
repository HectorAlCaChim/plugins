from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

from custom_api.services.course_access_role_service import (
    CourseAccessRoleService
)

from custom_api.serializers.UpdateCourseAccessRoleSerializer import (
    UpdateCourseAccessRoleSerializer
)


class CourseAccessRoleUpdateAPIView(APIView):

    @swagger_auto_schema(
        request_body=UpdateCourseAccessRoleSerializer,
        operation_description=(
            "Actualiza el rol del usuario en todos los cursos "
            "donde tenga asignaciones."
        )
    )
    def patch(self, request):

        open_edx_user_id = request.data.get(
            "openEdxUserId"
        )

        role = request.data.get(
            "role"
        )

        result = (
            CourseAccessRoleService
            .update_user_course_access_role(
                open_edx_user_id=open_edx_user_id,
                new_role=role
            )
        )

        return Response(
            result,
            status=result["status"]
        )