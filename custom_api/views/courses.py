from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication

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