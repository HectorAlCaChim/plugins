import math

from collections import defaultdict

from django.contrib.auth.models import User

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview
)

from lms.djangoapps.grades.models import (
    PersistentCourseGrade
)


class WorkshopCompletionService:

    STATUS_NOT_ENROLLED = "NOTENROLLED"
    STATUS_NO_COMPLETED = "NOCOMPLETED"
    STATUS_COMPLETED = "COMPLETED"

    def get_workshop_completion_status(
        self,
        users,
        passing_grade
    ):

        result = []

        #
        # Obtener todos los nombres de talleres
        #

        workshop_names = set()

        for item in users:
            workshop_names.update(
                item["workshopNames"]
            )

        #
        # Obtener todos los cursos
        #

        courses = CourseOverview.objects.filter(
            display_name__in=list(workshop_names)
        ).values(
            "id",
            "display_name"
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

        unresolved_emails = [
            x["email"]
            for x in users
            if not x.get("openEdxUserId")
        ]

        auth_users = User.objects.filter(
            email__in=unresolved_emails
        ).values(
            "id",
            "email"
        )

        users_by_email = {
            x["email"].lower(): x["id"]
            for x in auth_users
        }

        #
        # Obtener todos los user ids OpenEdX
        #

        all_user_ids = set()

        for item in users:

            user_id = item.get(
                "openEdxUserId"
            )

            if not user_id:

                user_id = users_by_email.get(
                    item["email"].lower()
                )

            if user_id:
                all_user_ids.add(user_id)

        #
        # Obtener todas las calificaciones
        #

        grades = PersistentCourseGrade.objects.filter(
            user_id__in=list(all_user_ids)
        ).values(
            "user_id",
            "course_id",
            "percent_grade"
        )

        grades_by_user = defaultdict(list)

        for grade in grades:
            grades_by_user[
                grade["user_id"]
            ].append(grade)

        #
        # Procesar
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
            # Equivalente a:
            # GetAuthUserByEmail == null
            #

            if not user_id:

                result.append({
                    "referenceId":
                        item["referenceId"],
                    "openEdxUserId":
                        None,
                    "completionStatus":
                        self.STATUS_NOT_ENROLLED
                })

                continue

            #
            # Equivalente a:
            # FindCourses
            #

            course_ids = []

            for workshop_name in item["workshopNames"]:

                course_ids.extend(
                    courses_by_name.get(
                        workshop_name,
                        []
                    )
                )

            if len(course_ids) == 0:

                result.append({
                    "referenceId":
                        item["referenceId"],
                    "openEdxUserId":
                        user_id,
                    "completionStatus":
                        self.STATUS_NOT_ENROLLED
                })

                continue

            #
            # Equivalente:
            # CompletionStatus = NOCOMPLETED
            #

            completion_status = (
                self.STATUS_NO_COMPLETED
            )

            grade_records = grades_by_user.get(
                user_id,
                []
            )

            if len(grade_records) == 0:

                result.append({
                    "referenceId":
                        item["referenceId"],
                    "openEdxUserId":
                        user_id,
                    "completionStatus":
                        completion_status
                })

                continue

            course_ids_set = set(course_ids)

            for grade in grade_records:

                if str(
                    grade["course_id"]
                ) not in course_ids_set:
                    continue

                percent = (
                    grade["percent_grade"]
                    or 0
                )

                #
                # EXACTAMENTE IGUAL A .NET
                #

                grade_number = math.ceil(
                    percent * 100
                )

                if grade_number >= passing_grade:

                    completion_status = (
                        self.STATUS_COMPLETED
                    )

                    break

            result.append({
                "referenceId":
                    item["referenceId"],
                "openEdxUserId":
                    user_id,
                "completionStatus":
                    completion_status
            })

        return result