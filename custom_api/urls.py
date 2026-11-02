from django.urls import path

from custom_api.views.courses import (
    CoursesAPIView,
    CourseNamesAPIView,
    ActiveCoursesAPIView
)
from custom_api.views.users import (
    UserStatusAPIView,
    BulkUserStatusAPIView,
    CreateUserAPIView,
    UpdateUserAPIView,
    GetUserByEmailAPIView,
    GetUserByIdAPIView,
    SearchUsersAPIView
)
from custom_api.views.instructors import (
    InstructorSearchAPIView
)
urlpatterns = [

    path(
        "courses/",
        CoursesAPIView.as_view(),
        name="courses"
    ),
    path(
        "course-names/",
        CourseNamesAPIView.as_view(),
        name="course_names"
    ),
    path(
        "active-courses/",
        ActiveCoursesAPIView.as_view(),
        name="active_courses"
    ),
     path(
        "users/<int:user_id>/status/",
        UserStatusAPIView.as_view(),
        name="user_status"
    ),
    path(
        "users/status/",
        BulkUserStatusAPIView.as_view(),
        name="bulk_user_status"
    ),
    path(
        "users/",
        CreateUserAPIView.as_view(),
        name="create_user"
    ),
    path(
        "users/<int:user_id>/",
        UpdateUserAPIView.as_view(),
        name="update_user"
    ),
    path(
        "users/",
        GetUserByEmailAPIView.as_view(),
        name="get_user_by_email"
    ),
     path(
        "users/by-id/",
        GetUserByIdAPIView.as_view(),
        name="get_user_by_id"
    ),
    path(
        "instructors/search/",
        InstructorSearchAPIView.as_view(),
        name="instructors_search"
    ),
    path(
        "users/search/",
        SearchUsersAPIView.as_view(),
        name="users_search"
    ),
]