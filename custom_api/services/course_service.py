# services/course_service.py
from datetime import datetime
from django.utils import timezone

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

class CourseService:
    #PRUEBA DE CONTROL PARA VALIDAR USO DE PLUGIN DE EXTENCION
    @staticmethod
    def get_all_courses():
        """
        Obtiene todos los cursos registrados
        en Open edX.

        Incluye cursos:
        - Activos
        - Finalizados
        - Futuros
        """

        try:

            courses = CourseOverview.objects.all().order_by(
                "display_name"
            )

            if not courses.exists():

                return {
                    "success": False,
                    "status": 404,
                    "message": "No courses found"
                }

            data = []

            for course in courses:

                data.append({
                    "id": str(course.id),
                    "displayName": course.display_name,
                    "shortDescription": getattr(
                        course,
                        "short_description",
                        None
                    ),
                    "version": getattr(
                        course,
                        "version",
                        None
                    ),
                    "start": course.start,
                    "end": course.end,
                    "enrollmentStart": course.enrollment_start,
                    "enrollmentEnd": course.enrollment_end,
                    "created": getattr(
                        course,
                        "created",
                        None
                    ),
                    "modified": getattr(
                        course,
                        "modified",
                        None
                    )
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
    # SE REALIZA UN CONSULTA DE SOLO LOS DISPLAY NAMES UNICOS DE LOS CURSOS DADO DE ALTA
    @staticmethod
    def get_unique_course_names():
        """
        Obtiene los nombres únicos de cursos
        ordenados ascendentemente.

        Retorna únicamente display_name.
        """

        try:

            names = list(
                CourseOverview.objects
                .values_list(
                    "display_name",
                    flat=True
                )
                .distinct()
                .order_by("display_name")
            )

            if not names:

                return {
                    "success": False,
                    "status": 404,
                    "message": "No courses found"
                }

            return {
                "success": True,
                "status": 200,
                "count": len(names),
                "data": names
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }
    # SE REALIZA UN VALIDACION DE QUE CURSOS SE PUEDEN SEGUIR PERMITIENDO ENROLAR ESTUIANTES SEGUN LA REGLA DEFINIDA
    @staticmethod
    def get_active_courses(max_days):

        now = timezone.now()

        active_courses = []

        courses = CourseOverview.objects.all().order_by("display_name")

        for course in courses:

            start = course.start
            end = course.end

            # Start = NULL && End = NULL
            if start is None and end is None:
                active_courses.append(course)
                continue

            # Start = NULL && End != NULL
            if start is None and end is not None:

                if now <= end:
                    active_courses.append(course)

                continue

            # Start != NULL && End = NULL
            if start is not None and end is None:

                if now >= start:
                    active_courses.append(course)
                    continue

                days_to_start = (start - now).days

                if days_to_start <= max_days:
                    active_courses.append(course)

                continue

            # Start != NULL && End != NULL

            if now < start:

                days_to_start = (start - now).days

                if days_to_start <= max_days and now <= end:
                    active_courses.append(course)

            elif start <= now <= end:

                active_courses.append(course)

        return active_courses
    