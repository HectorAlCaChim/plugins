from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from custom_api.services.course_access_role_service import (
    CourseAccessRoleService
)
from custom_api.serializers.UpdateCourseAccessRoleSerializer import (
    UpdateCourseAccessRoleSerializer
)


class CourseAccessRoleUpdateAPIView(APIView):

    @swagger_auto_schema(
        request_body=UpdateCourseAccessRoleSerializer,
        operation_description="Actualiza el rol de acceso de un usuario en un curso."
    )
    def patch(self, request, role_id):

        role = request.data.get("role")

        if not role:
            return Response(
                {
                    "detail": "role is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            CourseAccessRoleService.update_role(
                role_id=role_id,
                new_role=role.strip()
            )

            return Response(status=status.HTTP_200_OK)

        except ValueError as ex:

            if str(ex) == "ROLE_ASSIGNMENT_NOT_FOUND":
                return Response(
                    {
                        "detail": "Role assignment not found."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            if str(ex) == "DUPLICATE_ROLE_ASSIGNMENT":
                return Response(
                    {
                        "detail": "Role assignment already exists."
                    },
                    status=status.HTTP_409_CONFLICT
                )

            return Response(
                {
                    "detail": str(ex)
                },
                status=status.HTTP_400_BAD_REQUEST
            )