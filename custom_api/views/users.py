from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.permissions import AllowAny
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication

from custom_api.services.user_service import UserService


class AuthDebugView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "authorization_header": request.headers.get("Authorization"),
            "meta_authorization": request.META.get("HTTP_AUTHORIZATION"),
            "user": str(request.user),
            "is_authenticated": request.user.is_authenticated
        })


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication

from custom_api.services.user_service import UserService


class UserProfileAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):

        if not request.user.is_staff:

            return Response(
                {
                    "success": False,
                    "message": "Permission denied"
                },
                status=403
            )

        result = UserService.create_profile(
            user_id=user_id,
            name=request.data.get("name")
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

    def patch(self, request, user_id):

        if not request.user.is_staff:

            return Response(
                {
                    "success": False,
                    "message": "Permission denied"
                },
                status=403
            )

        result = UserService.update_profile_name(
            user_id=user_id,
            name=request.data.get("name")
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

    def get(self, request, user_id):

        if not request.user.is_staff:

            return Response(
                {
                    "success": False,
                    "message": "Permission denied"
                },
                status=403
            )

        result = UserService.get_profile(
            user_id=user_id
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

class UserStatusAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):

        is_active = request.data.get("isActive")

        if is_active is None:
            return Response({
                "success": False,
                "message": "isActive is required"
            }, status=400)

        result = UserService.update_user_status(
            user_id=user_id,
            is_active=is_active
        )

        if not result["success"]:

            if result["message"] == "User not found":
                return Response(result, status=404)

            return Response(result, status=400)

        return Response(result, status=200)


class BulkUserStatusAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):

        if not users:
            return Response({
                "success": False,
                "message": "users list is required"
            }, status=400)

        result = UserService.bulk_update_status(users)

        return Response({
            "success": True,
            "updated": result["updated"],
            "failed": result["failed"],
            "updated_users": result["updated_users"],
            "failed_users": result["failed_users"]
        }, status=200)

class CreateUserAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        result = UserService.create_user(
            username=request.data.get("userName"),
            password=request.data.get("password"),
            first_name=request.data.get("firstName"),
            last_name=request.data.get("lastName"),
            email=request.data.get("email"),
            is_superuser=request.data.get("isSuperuser", False),
            is_staff=request.data.get("isStaff", False),
            is_active=request.data.get("isActive", True)
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
            status=201
        )

class UpdateUserAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):


        result = UserService.update_user(
            user_id=user_id,
            username=request.data.get("userName"),
            password=request.data.get("password"),
            first_name=request.data.get("firstName"),
            last_name=request.data.get("lastName"),
            email=request.data.get("email"),
            is_superuser=request.data.get("isSuperuser"),
            is_staff=request.data.get("isStaff"),
            is_active=request.data.get("isActive")
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

class GetUserByEmailAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_staff:
            return Response(
                {
                    "success": False,
                    "message": "Permission denied"
                },
                status=403
            )

        email = request.GET.get("email")

        result = UserService.get_user_by_email(email)

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

class GetUserByIdAPIView(APIView):

    #authentication_classes = [JwtAuthentication]
    #permission_classes = [IsAuthenticated]
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        #if not request.user.is_staff:
            #return Response(
                #{
                    #"success": False,
                    #"message": "Permission denied"
                #},
                #status=403
            #)

        user_id = request.GET.get("userId")

        result = UserService.get_user_by_id(user_id)

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


class SearchUsersAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        #if not request.user.is_staff:

            #return Response(
                #{
                    #"success": False,
                    #"message": "Permission denied"
                #},
                #status=403
            #)

        result = UserService.get_all_users()

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

class UserPermissionsAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):

        if not request.user.is_staff:

            return Response(
                {
                    "success": False,
                    "message": "Permission denied"
                },
                status=403
            )

        result = UserService.has_course_admin_permissions(
            user_id
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

class UserCourseAccessRolesAPIView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):

        roles = request.GET.getlist(
            "role"
        )

        result = (
            UserService.get_course_access_roles(
                user_id=user_id,
                roles_filter=roles
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

class UserPasswordAPIView(APIView):

    #authentication_classes = [JwtAuthentication]
    #permission_classes = [IsAuthenticated]

    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):

        if not request.user.is_staff:

            return Response(
                {
                    "success": False,
                    "message": "Permission denied"
                },
                status=403
            )

        result = UserService.update_password(
            user_id=user_id,
            password=request.data.get(
                "password"
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