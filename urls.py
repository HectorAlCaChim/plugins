from django.urls import path

from openedx.plugins.custom_api.views.courses import (
    CoursesAPIView,
    CourseNamesAPIView,
    ActiveCoursesAPIView
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
]