# serializers/course_access_role.py

from rest_framework import serializers


class UpdateCourseAccessRoleSerializer(serializers.Serializer):
    role = serializers.CharField(
        required=True,
        help_text="Nuevo rol de acceso del usuario en el curso."
    )