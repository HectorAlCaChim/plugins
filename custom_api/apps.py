from django.apps import AppConfig


class CustomApiConfig(AppConfig):
    name = "custom_api"
    label = "custom_api"

    plugin_app = {
        "url_config": {
            "lms.djangoapp": {
                "namespace": "custom_api",
                "regex": r"^api/custom/v1/",
                "relative_path": "urls",
            }
        },
    }