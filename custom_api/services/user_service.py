from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from opaque_keys.edx.keys import CourseKey
from common.djangoapps.student.models import CourseAccessRole
import secrets
import string
User = get_user_model()
from common.djangoapps.student.roles import (
    CourseInstructorRole,
    CourseStaffRole
)
from openedx.core.djangoapps.content.course_overviews.models import (
    CourseOverview
)
try:
    from common.djangoapps.student.models import UserProfile
except Exception:
    UserProfile = None

User = get_user_model()


class UserService:

    @staticmethod
    def create_profile(
        user_id,
        name
    ):
        """
        Crea el registro UserProfile para un usuario.

        Regla:
        - Si ya existe UserProfile => 409 Conflict
        """

        if not name:

            return {
                "success": False,
                "status": 400,
                "message": "name is required"
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

            if not UserProfile:

                return {
                    "success": False,
                    "status": 503,
                    "message": "UserProfile service unavailable"
                }

            existing_profile = UserProfile.objects.filter(
                user=user
            ).first()

            if existing_profile:

                return {
                    "success": False,
                    "status": 409,
                    "message": "User profile already exists"
                }

            profile = UserProfile.objects.create(
                user=user,
                name=name
            )

            return {
                "success": True,
                "status": 200,
                "data": {
                    "id": user.id,
                    "name": profile.name,
                    "meta": getattr(
                        profile,
                        "meta",
                        ""
                    ),
                    "courseware": getattr(
                        profile,
                        "courseware",
                        ""
                    ),
                    "language": getattr(
                        profile,
                        "language",
                        ""
                    ),
                    "location": getattr(
                        profile,
                        "location",
                        ""
                    )
                }
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }

    @staticmethod
    def get_profile(user_id):
        """
        Obtiene la información del perfil de un usuario.
        """

        try:

            if not user_id:

                return {
                    "success": False,
                    "status": 400,
                    "message": "userId is required"
                }

            user = User.objects.filter(
                id=user_id
            ).first()

            if not user:

                return {
                    "success": False,
                    "status": 404,
                    "message": "User not found"
                }

            if not UserProfile:

                return {
                    "success": False,
                    "status": 503,
                    "message": "UserProfile service unavailable"
                }

            profile = UserProfile.objects.filter(
                user=user
            ).first()

            if not profile:

                return {
                    "success": False,
                    "status": 404,
                    "message": "Profile not found"
                }

            return {
                "success": True,
                "status": 200,
                "data": {
                    "id": user.id,
                    "name": profile.name,
                    "meta": profile.meta,
                    "courseware": profile.courseware,
                    "language": profile.language,
                    "location": profile.location
                }
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }

    @staticmethod
    def update_profile_name(
        user_id,
        name
    ):
        """
        Actualiza el nombre del perfil de un usuario.
        """

        if not name:

            return {
                "success": False,
                "status": 400,
                "message": "name is required"
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

            if not UserProfile:

                return {
                    "success": False,
                    "status": 503,
                    "message": "UserProfile service unavailable"
                }

            profile = UserProfile.objects.filter(
                user=user
            ).first()

            if not profile:

                return {
                    "success": False,
                    "status": 404,
                    "message": "Profile not found"
                }

            profile.name = name

            profile.save(
                update_fields=["name"]
            )

            return {
                "success": True,
                "status": 200,
                "data": {
                    "userId": user.id,
                    "name": profile.name,
                    "message": "Profile updated"
                }
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }

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

                generated_password = None

                if (
                    password is None
                    or str(password).strip() == ""
                ):

                    generated_password = (
                        UserService.generate_password()
                    )

                    user.set_password(
                        generated_password
                    )

                else:

                    user.set_password(
                        password
                    )

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

                generated_password = None

                if (
                    password is None
                    or str(password).strip() == ""
                ):

                    generated_password = (
                        UserService.generate_password()
                    )

                    user.set_password(
                        generated_password
                    )

                else:

                    user.set_password(
                        password
                    )
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
        Obtiene todos los usuarios registrados en Open edX.

        Incluye:
        - Roles globales
        - Roles de cursos

        Se devuelven separados para permitir filtros
        equivalentes a student_courseaccessrole.
        """

        try:

            users = User.objects.all().order_by("username")

            if not users.exists():
                return {
                    "success": False,
                    "status": 404,
                    "message": "No users found"
                }

            instructor_users = set()
            course_staff_users = set()

            #
            # Obtener usuarios con rol instructor
            # en una sola consulta
            #
            try:
                if CourseInstructorRole:
                    instructor_users = set(
                        CourseInstructorRole.objects.values_list(
                            "users__id",
                            flat=True
                        )
                    )
            except Exception:
                instructor_users = set()

            #
            # Obtener usuarios con rol course_staff
            # en una sola consulta
            #
            try:
                if CourseStaffRole:
                    course_staff_users = set(
                        CourseStaffRole.objects.values_list(
                            "users__id",
                            flat=True
                        )
                    )
            except Exception:
                course_staff_users = set()

            data = []

            for user in users:

                global_roles = [
                    "student"
                ]

                course_roles = []

                #
                # Roles globales
                #
                if user.is_staff:
                    global_roles.append("staff")

                if user.is_superuser:
                    global_roles.append("superuser")

                #
                # Roles de curso
                #
                if user.id in instructor_users:
                    course_roles.append("instructor")

                if user.id in course_staff_users:
                    course_roles.append("course_staff")

                #
                # Compatibilidad hacia atrás
                #
                all_roles = (
                    global_roles +
                    course_roles
                )

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

                    # Nuevo
                    "globalRoles": global_roles,
                    "courseRoles": course_roles,

                    # Compatibilidad
                    "roles": all_roles
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

    @staticmethod
    def has_course_admin_permissions(user_id):
        """
        Valida si un usuario posee permisos administrativos
        relacionados con la gestión de cursos.
        """

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

            permissions = [
                "content.courseoverview.add_courseoverview",
                "content.courseoverview.change_courseoverview",
                "content.courseoverview.delete_courseoverview",
                "content.courseoverview.view_courseoverview"
            ]

            has_permission = any(
                user.has_perm(permission)
                for permission in permissions
            )

            return {
                "success": True,
                "status": 200,
                "data": {
                    "userId": user.id,
                    "hasPermission": has_permission
                }
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }

    @staticmethod
    def get_course_access_roles(
        user_id,
        roles_filter=None
    ):
        """
        Obtiene los roles de acceso a cursos
        asignados a un usuario.
        """

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

            if roles_filter:
                roles_filter = [
                    role.lower()
                    for role in roles_filter
                ]

            assignments = []
            sequence = 1

            courses = CourseOverview.objects.all()

            for course in courses:

                course_roles = []

                course_key = course.id

                #
                # Instructor
                #
                try:

                    instructor_users = (
                        CourseInstructorRole(
                            course_key
                        ).users_with_role()
                    )

                    if any(
                        u.id == user.id
                        for u in instructor_users
                    ):
                        course_roles.append(
                            "instructor"
                        )

                except Exception:
                    pass

                #
                # Staff
                #
                try:

                    staff_users = (
                        CourseStaffRole(
                            course_key
                        ).users_with_role()
                    )

                    if any(
                        u.id == user.id
                        for u in staff_users
                    ):
                        course_roles.append(
                            "staff"
                        )

                except Exception:
                    pass

                for role in course_roles:

                    if (
                        roles_filter and
                        role not in roles_filter
                    ):
                        continue

                    assignments.append({
                        "id": sequence,
                        "userId": user.id,
                        "org": getattr(
                            course.id,
                            "org",
                            ""
                        ),
                        "courseId": str(
                            course.id
                        ),
                        "role": role
                    })

                    sequence += 1

            if not assignments:

                return {
                    "success": False,
                    "status": 404,
                    "message": "No course roles found"
                }

            return {
                "success": True,
                "status": 200,
                "count": len(assignments),
                "data": assignments
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }

    @staticmethod
    def add_course_access_role(
        open_edx_user_id,
        course_id,
        role
    ):
        """
        Asigna un rol de acceso a un curso.

        Si el rol ya existe para el usuario y curso,
        no se vuelve a insertar.
        """

        try:

            if not open_edx_user_id:

                return {
                    "success": False,
                    "status": 400,
                    "message": "openEdxUserId is required"
                }

            if not course_id:

                return {
                    "success": False,
                    "status": 400,
                    "message": "courseId is required"
                }

            if not role:

                return {
                    "success": False,
                    "status": 400,
                    "message": "role is required"
                }

            user = User.objects.filter(
                id=open_edx_user_id
            ).first()

            if user is None:

                return {
                    "success": False,
                    "status": 404,
                    "message": "User not found"
                }

            course_key = CourseKey.from_string(
                course_id
            )

            role = role.lower()

            #
            # Validación previa
            #
            existing_role = (
                CourseAccessRole.objects
                .filter(
                    user_id=open_edx_user_id,
                    course_id=course_key,
                    role=role
                )
                .first()
            )

            if existing_role:

                return {
                    "success": True,
                    "status": 200,
                    "message": "Role already assigned",
                    "data": {
                        "id": existing_role.id,
                        "userId": existing_role.user_id,
                        "courseId": str(
                            existing_role.course_id
                        ),
                        "org": existing_role.org,
                        "role": existing_role.role
                    }
                }

            access_role = (
                CourseAccessRole.objects.create(
                    user_id=open_edx_user_id,
                    course_id=course_key,
                    role=role,
                    org=course_key.org
                )
            )

            return {
                "success": True,
                "status": 200,
                "message": "Role assigned successfully",
                "data": {
                    "id": access_role.id,
                    "userId": access_role.user_id,
                    "courseId": str(
                        access_role.course_id
                    ),
                    "org": access_role.org,
                    "role": access_role.role
                }
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }

    @staticmethod
    def update_password(
        user_id,
        password
    ):
        """
        Actualiza la contraseña de un usuario
        Open edX.
        """

        if not password:

            return {
                "success": False,
                "status": 400,
                "message": "password is required"
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

            user.set_password(password)

            user.save(
                update_fields=["password"]
            )

            return {
                "success": True,
                "status": 200,
                "data": {
                    "userId": user.id,
                    "message": "Password updated successfully"
                }
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }

    @staticmethod
    def generate_password(length=12):

        chars = (
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits +
            "!@#$%&*"
        )

        password = (
            secrets.choice(string.ascii_uppercase)
            + secrets.choice(string.ascii_lowercase)
            + secrets.choice(string.digits)
            + secrets.choice("!@#$%&*")
        )

        for _ in range(length - 4):
            password += secrets.choice(chars)

        return password