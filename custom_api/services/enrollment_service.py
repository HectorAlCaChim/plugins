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

    @staticmethod
    def bulk_users_course_enrollment(users):

        if not users:
            return {
                "success": False,
                "status": 400,
                "message": "users is required"
            }

        try:

            usernames = set()
            course_keys_map = {}

            for item in users:

                username = item.get("user")

                if username:
                    usernames.add(username)

                for course_id in (
                    item.get("courseIds") or []
                ):

                    if not course_id:
                        continue

                    try:

                        if (
                            course_id
                            not in course_keys_map
                        ):

                            course_keys_map[
                                course_id
                            ] = (
                                CourseKey.from_string(
                                    course_id
                                )
                            )

                    except Exception:
                        pass

            users_map = {
                user.username: user
                for user in User.objects.filter(
                    username__in=usernames
                )
            }

            existing_courses = {
                str(course.id): course.id
                for course in (
                    CourseOverview.objects.filter(
                        id__in=course_keys_map.values()
                    )
                )
            }

            user_ids = [
                user.id
                for user in users_map.values()
            ]

            existing_enrollments = {
                (
                    enrollment.user_id,
                    str(enrollment.course_id)
                )
                for enrollment in (
                    CourseEnrollment.objects.filter(
                        user_id__in=user_ids,
                        course_id__in=existing_courses.values()
                    )
                )
            }

            summary = {
                "usersProcessed": 0,
                "processed": 0,
                "assigned": 0,
                "unassigned": 0,
                "skipped": 0,
                "failed": 0,
                "details": []
            }

            for item in users:

                username = item.get("user")
                action = item.get("action")
                course_ids = item.get("courseIds")

                summary["usersProcessed"] += 1

                if not username:

                    summary["failed"] += 1

                    summary["details"].append({
                        "user": None,
                        "action": action,
                        "success": False,
                        "message": "user is required"
                    })

                    continue

                if action not in [
                    "assign",
                    "unassign"
                ]:

                    summary["failed"] += 1

                    summary["details"].append({
                        "user": username,
                        "action": action,
                        "success": False,
                        "message":
                            "action must be assign or unassign"
                    })

                    continue

                if not course_ids:

                    summary["failed"] += 1

                    summary["details"].append({
                        "user": username,
                        "action": action,
                        "success": False,
                        "message": "courseIds is required"
                    })

                    continue

                user = users_map.get(
                    username
                )

                if not user:

                    summary["failed"] += 1

                    summary["details"].append({
                        "user": username,
                        "action": action,
                        "success": False,
                        "message": "User not found"
                    })

                    continue

                user_processed = 0
                user_assigned = 0
                user_unassigned = 0
                user_skipped = 0
                user_failed = 0

                errors = []

                for course_id in course_ids:

                    try:

                        course_key = (
                            course_keys_map.get(
                                course_id
                            )
                        )

                        if (
                            not course_key
                            or str(course_key)
                            not in existing_courses
                        ):

                            user_failed += 1

                            errors.append({
                                "courseId": course_id,
                                "error": "Course not found"
                            })

                            continue

                        enrollment_key = (
                            user.id,
                            str(course_key)
                        )

                        is_enrolled = (
                            enrollment_key
                            in existing_enrollments
                        )

                        if action == "assign":

                            if is_enrolled:

                                user_skipped += 1

                                continue

                            CourseEnrollment.enroll(
                                user,
                                course_key
                            )

                            existing_enrollments.add(
                                enrollment_key
                            )

                            user_assigned += 1
                            user_processed += 1

                        else:

                            if not is_enrolled:

                                user_skipped += 1

                                continue

                            CourseEnrollment.unenroll(
                                user,
                                course_key
                            )

                            existing_enrollments.discard(
                                enrollment_key
                            )

                            user_unassigned += 1
                            user_processed += 1

                    except Exception as ex:

                        user_failed += 1

                        errors.append({
                            "courseId": course_id,
                            "error": str(ex)
                        })

                summary["processed"] += (
                    user_processed
                )

                summary["assigned"] += (
                    user_assigned
                )

                summary["unassigned"] += (
                    user_unassigned
                )

                summary["skipped"] += (
                    user_skipped
                )

                summary["failed"] += (
                    user_failed
                )

                summary["details"].append({
                    "user": username,
                    "action": action,
                    "success": (
                        user_failed == 0
                    ),
                    "processed": (
                        user_processed
                    ),
                    "assigned": (
                        user_assigned
                    ),
                    "unassigned": (
                        user_unassigned
                    ),
                    "skipped": (
                        user_skipped
                    ),
                    "failed": (
                        user_failed
                    ),
                    "errors": errors
                })

            return {
                "success": True,
                "status": 200,
                "data": summary
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }