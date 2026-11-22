from django.db import transaction
from common.djangoapps.student.models import CourseAccessRole


class CourseAccessRoleService(object):

    @staticmethod
    @transaction.atomic
    def update_role(role_id, new_role):

        try:
            access_role = CourseAccessRole.objects.select_for_update().get(
                pk=role_id
            )

        except CourseAccessRole.DoesNotExist:
            raise ValueError("ROLE_ASSIGNMENT_NOT_FOUND")

        if access_role.role == new_role:
            return

        duplicate_exists = CourseAccessRole.objects.filter(
            user=access_role.user,
            course_id=access_role.course_id,
            org=access_role.org,
            role=new_role
        ).exclude(
            pk=access_role.id
        ).exists()

        if duplicate_exists:
            raise ValueError("DUPLICATE_ROLE_ASSIGNMENT")

        access_role.role = new_role
        access_role.save(update_fields=["role"])