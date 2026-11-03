from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from common.djangoapps.student.roles import (
    CourseInstructorRole,
    CourseStaffRole
)

try:
    from common.djangoapps.student.models import UserProfile
except Exception:
    UserProfile = None

User = get_user_model()


class UserService:

    @staticmethod
    def update_user_status(user_id, is_active):
        try:
            user = User.objects.filter(id=user_id).first()

            if not user:
                return {
                    "success": False,
                    "user_id": user_id,
                    "message": "User not found"
                }

            if user.is_superuser:
                return {
                    "success": False,
                    "user_id": user_id,
                    "message": "Cannot update superuser"
                }

            user.is_active = is_active
            user.save(update_fields=["is_active"])

            return {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "is_active": user.is_active
            }

        except Exception as ex:
            return {
                "success": False,
                "user_id": user_id,
                "message": str(ex)
            }

    @staticmethod
    def bulk_update_status(users):
        updated = []
        failed = []

        for item in users:

            user_id = item.get("userId")
            is_active = item.get("isActive")

            result = UserService.update_user_status(
                user_id=user_id,
                is_active=is_active
            )

            if result["success"]:
                updated.append(result)
            else:
                failed.append(result)

        return {
            "updated": len(updated),
            "failed": len(failed),
            "updated_users": updated,
            "failed_users": failed
        }

    @staticmethod
    def create_user(
        username,
        password,
        first_name,
        last_name,
        email,
        is_superuser=False,
        is_staff=False,
        is_active=True
    ):

        if not username:
            return {
                "success": False,
                "status": 400,
                "message": "userName is required"
            }

        if not password:
            return {
                "success": False,
                "status": 400,
                "message": "password is required"
            }

        if not first_name:
            return {
                "success": False,
                "status": 400,
                "message": "firstName is required"
            }

        if not last_name:
            return {
                "success": False,
                "status": 400,
                "message": "lastName is required"
            }

        if not email:
            return {
                "success": False,
                "status": 400,
                "message": "email is required"
            }

        try:
            validate_email(email)
        except ValidationError:
            return {
                "success": False,
                "status": 400,
                "message": "invalid email format"
            }

        if User.objects.filter(username__iexact=username).exists():
            return {
                "success": False,
                "status": 409,
                "message": "username already exists"
            }

        if User.objects.filter(email__iexact=email).exists():
            return {
                "success": False,
                "status": 409,
                "message": "email already exists"
            }

        try:

            with transaction.atomic():

                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    is_superuser=is_superuser,
                    is_staff=is_staff,
                    is_active=is_active
                )

                user.set_password(password)

                user.save()

                #
                # Protección para Open edX Ulmo
                #
                if UserProfile:

                    exists_profile = UserProfile.objects.filter(
                        user=user
                    ).exists()

                    if not exists_profile:
                        UserProfile.objects.create(
                            user=user
                        )

                return {
                    "success": True,
                    "status": 201,
                    "data": {
                        "id": user.id,
                        "userName": user.username,
                        "email": user.email,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "isSuperuser": user.is_superuser,
                        "isStaff": user.is_staff,
                        "isActive": user.is_active,
                        "dateJoined": user.date_joined
                    }
                }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }

    @staticmethod
    def update_user(
        user_id,
        username,
        password,
        first_name,
        last_name,
        email,
        is_superuser,
        is_staff,
        is_active
    ):

        user = User.objects.filter(id=user_id).first()

        if not user:
            return {
                "success": False,
                "status": 404,
                "message": "User not found"
            }

        if not username:
            return {
                "success": False,
                "status": 400,
                "message": "userName is required"
            }

        if not password:
            return {
                "success": False,
                "status": 400,
                "message": "password is required"
            }

        if not first_name:
            return {
                "success": False,
                "status": 400,
                "message": "firstName is required"
            }

        if not last_name:
            return {
                "success": False,
                "status": 400,
                "message": "lastName is required"
            }

        if not email:
            return {
                "success": False,
                "status": 400,
                "message": "email is required"
            }

        try:
            validate_email(email)
        except ValidationError:
            return {
                "success": False,
                "status": 400,
                "message": "invalid email format"
            }

        username_exists = User.objects.filter(
            username__iexact=username
        ).exclude(id=user_id).exists()

        if username_exists:
            return {
                "success": False,
                "status": 409,
                "message": "username already exists"
            }

        email_exists = User.objects.filter(
            email__iexact=email
        ).exclude(id=user_id).exists()

        if email_exists:
            return {
                "success": False,
                "status": 409,
                "message": "email already exists"
            }

        try:

            with transaction.atomic():

                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.is_superuser = is_superuser
                user.is_staff = is_staff
                user.is_active = is_active

                user.set_password(password)

                user.save()

                return {
                    "success": True,
                    "status": 200,
                    "data": {
                        "id": user.id,
                        "userName": user.username,
                        "email": user.email,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "isSuperuser": user.is_superuser,
                        "isStaff": user.is_staff,
                        "isActive": user.is_active,
                        "dateJoined": user.date_joined
                    }
                }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }

    @staticmethod
    def get_user_by_email(email):
        """
        Obtiene la información de un usuario a partir de su email.

        Args:
            email (str)

        Returns:
            dict
        """

        if not email:
            return {
                "success": False,
                "status": 400,
                "message": "email is required"
            }

        try:
            validate_email(email)
        except ValidationError:
            return {
                "success": False,
                "status": 400,
                "message": "invalid email format"
            }

        try:

            user = User.objects.filter(
                email__iexact=email
            ).first()

            if not user:
                return {
                    "success": False,
                    "status": 404,
                    "message": "User not found"
                }

            return {
                "success": True,
                "status": 200,
                "data": {
                    "id": user.id,
                    "userName": user.username,

                    # No recomendado exponer
                    # "password": user.password,

                    "email": user.email,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "isSuperuser": user.is_superuser,
                    "isStaff": user.is_staff,
                    "isActive": user.is_active,
                    "lastLogin": user.last_login,
                    "dateJoined": user.date_joined
                }
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }

    @staticmethod
    def get_user_by_id(user_id):
        """
        Obtiene la información de un usuario
        a partir de su identificador.

        Args:
            user_id (int)

        Returns:
            dict
        """

        if user_id is None:
            return {
                "success": False,
                "status": 400,
                "message": "userId is required"
            }

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return {
                "success": False,
                "status": 400,
                "message": "userId must be numeric"
            }

        try:

            user = User.objects.filter(
                id=user_id
            ).first()

            if not user:
                return {
                    "success": False,
                    "status": 404,
                    "message": "User not found"
                }

            return {
                "success": True,
                "status": 200,
                "data": {
                    "id": user.id,
                    "userName": user.username,
                    "email": user.email,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "isSuperuser": user.is_superuser,
                    "isStaff": user.is_staff,
                    "isActive": user.is_active,
                    "lastLogin": user.last_login,
                    "dateJoined": user.date_joined
                }
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }
    @staticmethod
    def get_all_users():
        """
        Obtiene todos los usuarios registrados
        en Open edX.

        Incluye roles globales y de cursos.
        """

        try:

            users = User.objects.all().order_by("username")

            if not users.exists():

                return {
                    "success": False,
                    "status": 404,
                    "message": "No users found"
                }

            data = []

            for user in users:

                roles = []

                #
                # Todo usuario se considera student.
                #
                roles.append("student")

                if user.is_staff:
                    roles.append("staff")

                if user.is_superuser:
                    roles.append("superuser")

                try:

                    has_instructor_role = (
                        CourseInstructorRole.objects.filter(
                            users=user
                        ).exists()
                    )

                    if has_instructor_role:
                        roles.append("instructor")

                except Exception:
                    pass

                try:

                    has_course_staff_role = (
                        CourseStaffRole.objects.filter(
                            users=user
                        ).exists()
                    )

                    if (
                        has_course_staff_role and
                        "course_staff" not in roles
                    ):
                        roles.append("course_staff")

                except Exception:
                    pass

                data.append({
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
                    "roles": roles
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