from rest_framework import serializers


class UpdateCourseAccessRoleSerializer(
    serializers.Serializer
):

    openEdxUserId = serializers.IntegerField()

    role = serializers.ChoiceField(
        choices=[
            "student",
            "instructor"
        ]
    )