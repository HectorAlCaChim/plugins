import math

from collections import defaultdict

from django.contrib.auth.models import User

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview
)

from lms.djangoapps.grades.models import (
    PersistentCourseGrade
)


class WorkshopCompletionGroupBulkService:

    STATUS_NOT_ENROLLED = "NOTENROLLED"
    STATUS_NO_COMPLETED = "NOCOMPLETED"
    STATUS_COMPLETED = "COMPLETED"

    @classmethod
    def get_completion_status(
        cls,
        users,
        passing_grade
    ):
        try:

            result = []

            #
            # Cursos únicos
            #
            workshop_names = set()

            for item in users:
                workshop_names.update(
                    item["workshopNames"]
                )

            courses = (
                CourseOverview.objects
                .filter(
                    display_name__in=list(workshop_names)
                )
                .values(
                    "id",
                    "display_name"
                )
            )

            courses_by_name = defaultdict(list)

            for course in courses:
                courses_by_name[
                    course["display_name"]
                ].append(
                    str(course["id"])
                )

            #
            # Resolver usuarios por email
            #
            emails = {
                x["email"].lower()
                for x in users
                if not x.get("openEdxUserId")
            }

            auth_users = (
                User.objects
                .filter(
                    email__in=list(emails)
                )
                .values(
                    "id",
                    "email"
                )
            )

            users_by_email = {
                x["email"].lower(): x["id"]
                for x in auth_users
            }

            #
            # Usuarios OpenEdX
            #
            open_edx_ids = set()

            for item in users:

                user_id = item.get(
                    "openEdxUserId"
                )

                if not user_id:
                    user_id = users_by_email.get(
                        item["email"].lower()
                    )

                if user_id:
                    open_edx_ids.add(user_id)

            #
            # Todas las calificaciones en una consulta
            #
            grades = (
                PersistentCourseGrade.objects
                .filter(
                    user_id__in=list(open_edx_ids)
                )
                .values(
                    "user_id",
                    "course_id",
                    "percent_grade"
                )
            )

            grades_by_user = defaultdict(list)

            for grade in grades:

                grades_by_user[
                    grade["user_id"]
                ].append(
                    grade
                )

            #
            # Procesamiento
            #
            for item in users:

                user_id = item.get(
                    "openEdxUserId"
                )

                if not user_id:
                    user_id = users_by_email.get(
                        item["email"].lower()
                    )

                #
                # Equivalente a
                # usuario no encontrado
                #
                if not user_id:

                    result.append({
                        "referenceId":
                            item["referenceId"],

                        "completionStatus":
                            cls.STATUS_NOT_ENROLLED
                    })

                    continue

                course_ids = []

                for workshop_name in item["workshopNames"]:

                    course_ids.extend(
                        courses_by_name.get(
                            workshop_name,
                            []
                        )
                    )

                #
                # Equivalente a
                # cursos no encontrados
                #
                if len(course_ids) == 0:

                    result.append({
                        "referenceId":
                            item["referenceId"],

                        "completionStatus":
                            cls.STATUS_NOT_ENROLLED
                    })

                    continue

                completion_status = (
                    cls.STATUS_NO_COMPLETED
                )

                grades_for_user = (
                    grades_by_user.get(
                        user_id,
                        []
                    )
                )

                course_ids_set = (
                    set(course_ids)
                )

                for grade in grades_for_user:

                    if str(
                        grade["course_id"]
                    ) not in course_ids_set:
                        continue

                    percent = (
                        grade["percent_grade"]
                        or 0
                    )

                    #
                    # EXACTAMENTE IGUAL AL .NET
                    #
                    grade_number = math.ceil(
                        percent * 100
                    )

                    if (
                        grade_number >=
                        passing_grade
                    ):
                        completion_status = (
                            cls.STATUS_COMPLETED
                        )
                        break

                result.append({
                    "referenceId":
                        item["referenceId"],

                    "completionStatus":
                        completion_status
                })

            return {
                "success": True,
                "status": 200,
                "count": len(result),
                "data": result
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }