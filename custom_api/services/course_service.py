# services/course_service.py
from datetime import datetime
from django.utils import timezone

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

class CourseService:
    #PRUEBA DE CONTROL PARA VALIDAR USO DE PLUGIN DE EXTENCION
    @staticmethod
    def get_courses():
        return [
            {
                "course_id": "course-v1:BWA21+00021+2026_T1",
                "display_name": "Curso Demo"
            }
        ]
    # SE REALIZA UN CONSULTA DE SOLO LOS DISPLAY NAMES UNICOS DE LOS CURSOS DADO DE ALTA
    @staticmethod
    def get_unique_course_names():

        return (
            CourseOverview.objects
            .values_list("display_name", flat=True)
            .distinct()
            .order_by("display_name")
        )
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
    