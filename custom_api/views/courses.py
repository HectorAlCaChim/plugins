from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from custom_api.services.course_service import CourseService

class SearchCoursesAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        result = CourseService.get_all_courses()

        if not result["success"]:

            return Response(
                {
                    "success": False,
                    "message": result["message"]
                },
                status=result["status"]
            )

        return Response(
            result["data"],
            status=200
        )
## SE COSULTA EL CATALOGO DE DISPLAY NAMES DE LOS CURSOS EXISTENTES##
class CourseNamesAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        result = CourseService.get_unique_course_names()

        if not result["success"]:

            return Response(
                {
                    "success": False,
                    "message": result["message"]
                },
                status=result["status"]
            )

        return Response(
            result["data"],
            status=200
        )

#SE CONSULTAN TODOS LOS CURSOS ACTIVOS SEGUN UNA REGLA DEFINIDA
class ActiveCoursesAPIView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):

        max_days = request.GET.get("max_days")

        if not max_days:
            return Response({
                "success": False,
                "message": "El parámetro max_days es requerido."
            }, status=400)

        try:
            max_days = int(max_days)
        except ValueError:
            return Response({
                "success": False,
                "message": "max_days debe ser un número entero."
            }, status=400)

        courses = CourseService.get_active_courses(max_days)

        data = []

        for course in courses:

            data.append({
                "course_id": str(course.id),
                "display_name": course.display_name,
                "start": course.start,
                "end": course.end,
                "enrollment_start": course.enrollment_start,
                "enrollment_end": course.enrollment_end
            })

        return Response({
            "success": True,
            "count": len(data),
            "data": data
        })

class CoursesByDisplayNamesAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]


    def post(self, request):

        workshop_names = request.data.get(
            "workshopNames"
        )

        result = (
            CourseService.get_courses_by_display_names(
                workshop_names
            )
        )

        if not result["success"]:

            return Response(
                {
                    "success": False,
                    "message": result["message"]
                },
                status=result["status"]
            )

        return Response(
            result["data"],
            status=200
        )


class FindCourseByIdAPIView(APIView):

    #authentication_classes = [OAuth2Authentication]
    #permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Consultar un curso por su identificador",
        operation_description=(
            "Consulta un curso de Open edX mediante su identificador completo."
        ),
        manual_parameters=[
            openapi.Parameter(
                name="course_id",
                in_=openapi.IN_PATH,
                description=(
                    "Identificador completo del curso. "
                    "Ejemplo: course-v1:LED-2026-05+FINAN-002E+BW"
                ),
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def get(self, request, course_id):

        if not course_id:

            return Response(
                {
                    "detail": "El identificador tiene un formato inválido."
                },
                status=400
            )

        result = CourseService.get_course_by_id(
            course_id
        )

        if not result["success"]:

            if result["status"] == 404:

                return Response(
                    {
                        "detail": "No existe el curso solicitado."
                    },
                    status=404
                )

            if result["status"] == 400:

                return Response(
                    {
                        "detail": "El identificador tiene un formato inválido."
                    },
                    status=400
                )

            return Response(
                {
                    "detail": result["message"]
                },
                status=result["status"]
            )

        return Response(
            result["data"],
            status=200
        )