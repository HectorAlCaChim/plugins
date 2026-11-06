from django.contrib.auth import get_user_model

from lms.djangoapps.grades.models import (
    PersistentCourseGrade
)

User = get_user_model()


class GradeService:

    @staticmethod
    def get_student_grades(
        open_edx_user_id,
        course_ids
    ):
        """
        Obtiene las calificaciones persistidas
        de un estudiante para los cursos solicitados.
        """

        if not open_edx_user_id:

            return {
                "success": False,
                "status": 400,
                "message": "openEdxUserId is required"
            }

        if not course_ids:

            return {
                "success": False,
                "status": 400,
                "message": "courseIds is required"
            }

        try:

            user_exists = User.objects.filter(
                id=open_edx_user_id
            ).exists()

            if not user_exists:

                return {
                    "success": False,
                    "status": 404,
                    "message": "User not found"
                }

            grades = (
                PersistentCourseGrade.objects
                .filter(
                    user_id=open_edx_user_id,
                    course_id__in=course_ids
                )
                .order_by("created")
            )

            if not grades.exists():

                return {
                    "success": False,
                    "status": 404,
                    "message": "No grades found"
                }

            data = []

            for grade in grades:

                data.append({
                    "created": (
                        grade.created.isoformat()
                        if grade.created
                        else None
                    ),
                    "userId": int(grade.user_id),
                    "courseId": str(grade.course_id),
                    "percentGrade": (
                        float(grade.percent_grade)
                        if grade.percent_grade is not None
                        else None
                    ),
                    "letterGrade": grade.letter_grade
                })

            return {
                "success": True,
                "status": 200,
                "count": len(data),
                "data": data
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }