from opaque_keys.edx.keys import CourseKey

from common.djangoapps.student.roles import (
    CourseInstructorRole
)

from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview
)


class InstructorService:

    @staticmethod
    def get_instructors(course_ids=None):
        """
        Obtiene los instructores asociados a los cursos indicados.

        Si course_ids es None o viene vacío,
        se consultan todos los cursos existentes.

        Retorna cada instructor una sola vez y
        agrega el listado de courseIds donde
        tiene asignado el rol Instructor.
        """

        instructors = {}

        try:

            # Consultar todos los cursos si no se reciben filtros.
            if not course_ids:

                course_ids = [
                    str(course.id)
                    for course in CourseOverview.objects.all()
                ]

            for course_id in course_ids:

                try:

                    course_key = CourseKey.from_string(
                        str(course_id)
                    )

                    instructor_users = (
                        CourseInstructorRole(
                            course_key
                        ).users_with_role()
                    )

                    for user in instructor_users:

                        if user.id not in instructors:

                            instructors[user.id] = {
                                "id": user.id,
                                "userName": user.username,
                                "email": user.email,
                                "firstName": user.first_name,
                                "lastName": user.last_name,
                                "isSuperuser": user.is_superuser,
                                "isStaff": user.is_staff,
                                "isActive": user.is_active,
                                "lastLogin": user.last_login,
                                "dateJoined": user.date_joined,
                                "courses": []
                            }

                        # Evitar duplicados de cursos
                        if course_id not in instructors[user.id]["courses"]:

                            instructors[user.id]["courses"].append(
                                str(course_id)
                            )

                except Exception:
                    continue

            if not instructors:

                return {
                    "success": False,
                    "status": 404,
                    "message": "No instructors found"
                }

            return {
                "success": True,
                "status": 200,
                "count": len(instructors),
                "data": list(instructors.values())
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }