from django.urls import path
from custom_api.views.enrollments import (
    BulkCourseEnrollmentAPIView
)
from custom_api.views.courses import (
    CourseNamesAPIView,
    ActiveCoursesAPIView,
    SearchCoursesAPIView,
    CoursesByDisplayNamesAPIView
)
from custom_api.views.users import (
    UserStatusAPIView,
    BulkUserStatusAPIView,
    CreateUserAPIView,
    UpdateUserAPIView,
    GetUserByEmailAPIView,
    GetUserByIdAPIView,
    SearchUsersAPIView,
    UserPermissionsAPIView,
    AuthDebugView,
    UserCourseAccessRolesAPIView,
    UserPasswordAPIView,
    UserProfileDetailAPIView,
    UserProfileCreateAPIView,
    UserProfileUpdateAPIView
)
from custom_api.views.instructors import (
    InstructorSearchAPIView
)
urlpatterns = [
    #18. Crear perfil de usuario
    #20. actualizar el nombre del perfil
    #19. Consultar perfil de usuario
    path(
        "users/<int:user_id>/profile/",
        UserProfileAPIView.as_view(),
        name="user_profile"
    ),
    path(
        'api/custom/debug/auth',
        AuthDebugView.as_view(),
        name='auth-debug'
    ),
    #11. Consular lista de cursos
    path(
        "courses/search/",
        SearchCoursesAPIView.as_view(),
        name="courses_search"
    ),
    #12. Consultar listado de nombres únicos de cursos
    path(
        "courses/names/",
        CourseNamesAPIView.as_view(),
        name="course_names"
    ),
    #16. Consultar cursos por nombre de taller
    path(
        "courses/display_names/",
        CoursesByDisplayNamesAPIView.as_view(),
        name="courses_display_names"
    ),
    path(
        "active-courses/",
        ActiveCoursesAPIView.as_view(),
        name="active_courses"
    ),
    #2. Actulizar Contraseña
    path(
        "users/<int:user_id>/password/",
        UserPasswordAPIView.as_view(),
        name="user_password"
    ),
    #3. Actualizar estado del usuario
     path(
        "users/<int:user_id>/status/",
        UserStatusAPIView.as_view(),
        name="user_status"
    ),
    #4. Actualizar estado de un conjunto de usuarios
    path(
        "users/status/",
        BulkUserStatusAPIView.as_view(),
        name="bulk_user_status"
    ),
    #1. Crear Usuario
    path(
        "users/",
        CreateUserAPIView.as_view(),
        name="create_user"
    ),
    #5. Actualizar información del usuario
    path(
        "users/<int:user_id>/",
        UpdateUserAPIView.as_view(),
        name="update_user"
    ),
    #6. Solicitar información de un usuario por email
    path(
        "users/by-email/",
        GetUserByEmailAPIView.as_view(),
        name="get_user_by_email"
    ),
    #7. Consultar información del usuario por ID
     path(
        "users/by-id/",
        GetUserByIdAPIView.as_view(),
        name="get_user_by_id"
    ),
    #15. Obtiene los roles de acceso asignados a un usuario en los cursos de Open edX.
    path(
        "users/<int:user_id>/course-access-roles/",
        UserCourseAccessRolesAPIView.as_view(),
        name="user_course_access_roles"
    ),
    # 17. Asignar y desasignar de uno o más cursos
    path(
        "users/course-enrollments/bulk/",
        BulkCourseEnrollmentAPIView.as_view(),
        name="bulk_course_enrollment"
    ),
    #8 Consultar todos los instructores de los cursos proporcionados
    path(
        "instructors/search/",
        InstructorSearchAPIView.as_view(),
        name="instructors_search"
    ),
    #9. Consultar usuarios del sistema
    path(
        "users/search/",
        SearchUsersAPIView.as_view(),
        name="users_search"
    ),
    #10. Valida si un usuario posee permisos de administración de cursos en Open edX.
    path(
        "users/<int:user_id>/permissions/",
        UserPermissionsAPIView.as_view(),
        name="user_permissions"
    ),
]