from django.contrib.auth import get_user_model

from opaque_keys.edx.keys import CourseKey

from common.djangoapps.student.models import (
    CourseEnrollment
)

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview
)

User = get_user_model()


class EnrollmentService:

    @staticmethod
    def bulk_course_enrollment(
        username,
        action,
        course_ids
    ):
        """
        Asigna o desasigna múltiples cursos
        a un usuario.
        """

        if not username:
            return {
                "success": False,
                "status": 400,
                "message": "user is required"
            }

        if action not in [
            "assign",
            "unassign"
        ]:
            return {
                "success": False,
                "status": 400,
                "message": "action must be assign or unassign"
            }

        if not course_ids:
            return {
                "success": False,
                "status": 400,
                "message": "courseIds is required"
            }

        try:

            user = User.objects.filter(
                username=username
            ).first()

            if not user:
                return {
                    "success": False,
                    "status": 404,
                    "message": "User not found"
                }

            processed = 0
            assigned = 0
            unassigned = 0
            failed = 0
            errors = []

            for course_id in course_ids:

                try:

                    course_key = (
                        CourseKey.from_string(
                            course_id
                        )
                    )

                    course_exists = (
                        CourseOverview.objects.filter(
                            id=course_key
                        ).exists()
                    )

                    if not course_exists:

                        failed += 1

                        errors.append({
                            "courseId": course_id,
                            "error": "Course not found"
                        })

                        continue

                    if action == "assign":

                        CourseEnrollment.enroll(
                            user,
                            course_key
                        )

                        assigned += 1

                    else:

                        CourseEnrollment.unenroll(
                            user,
                            course_key
                        )

                        unassigned += 1

                    processed += 1

                except Exception as ex:

                    failed += 1

                    errors.append({
                        "courseId": course_id,
                        "error": str(ex)
                    })

            return {
                "success": True,
                "status": 200,
                "data": {
                    "processed": processed,
                    "assigned": assigned,
                    "unassigned": unassigned,
                    "failed": failed,
                    "errors": errors
                }
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }