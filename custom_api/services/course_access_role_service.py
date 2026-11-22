from django.contrib.auth.models import User
from django.db import transaction

from opaque_keys.edx.keys import CourseKey

from common.djangoapps.student.models import CourseAccessRole


class CourseAccessRoleService(object):

    @staticmethod
    @transaction.atomic
    def update_user_course_access_role(
        open_edx_user_id,
        new_role
    ):
        try:

            if not open_edx_user_id:
                return {
                    "success": False,
                    "status": 400,
                    "message": "openEdxUserId is required"
                }

            if not new_role:
                return {
                    "success": False,
                    "status": 400,
                    "message": "newRole is required"
                }

            new_role = new_role.lower().strip()

            if new_role not in ["student", "instructor"]:
                return {
                    "success": False,
                    "status": 400,
                    "message": "Invalid role"
                }

            user = User.objects.filter(
                id=open_edx_user_id
            ).first()

            if not user:
                return {
                    "success": False,
                    "status": 404,
                    "message": "User not found"
                }

            updated_count = (
                CourseAccessRole.objects
                .filter(
                    user_id=open_edx_user_id
                )
                .update(
                    role=new_role
                )
            )

            return {
                "success": True,
                "status": 200,
                "message": "Roles updated successfully",
                "data": {
                    "userId": open_edx_user_id,
                    "newRole": new_role,
                    "updatedRecords": updated_count
                }
            }

        except Exception as ex:

            return {
                "success": False,
                "status": 500,
                "message": str(ex)
            }