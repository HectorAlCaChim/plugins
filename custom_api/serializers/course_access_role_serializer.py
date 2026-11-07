# serializers/course_access_role_serializer.py

from rest_framework import serializers


class CourseAccessRoleRequestSerializer(
    serializers.Serializer
):

    openEdxUserId = serializers.IntegerField(
        required=True
    )

    courseId = serializers.CharField(
        required=True
    )

    role = serializers.CharField(
        required=True
    )