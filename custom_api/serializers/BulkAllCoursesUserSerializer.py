from rest_framework import serializers


class BulkAllCoursesUserSerializer(
    serializers.Serializer
):
    user = serializers.CharField(
        required=False
    )

    email = serializers.EmailField(
        required=False
    )

    action = serializers.ChoiceField(
        choices=[
            "assign",
            "unassign"
        ]
    )

    def validate(self, attrs):

        if not attrs.get("user") and \
           not attrs.get("email"):
            raise serializers.ValidationError(
                "user or email is required"
            )

        return attrs