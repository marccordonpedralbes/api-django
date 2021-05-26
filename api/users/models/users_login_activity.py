from api.utils.models import CModel
from django.db import models


class UserLoginActivity(CModel):
    # Login Status

    SUCCESS = "S"

    FAILED = "F"

    LOGIN_STATUS = ((SUCCESS, "Success"), (FAILED, "Failed"))

    login_IP = models.GenericIPAddressField(null=True, blank=True)
    login_datetime = models.DateTimeField(auto_now=True)
    login_username = models.CharField(max_length=40, null=True, blank=True)
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, default=SUCCESS, choices=LOGIN_STATUS, null=True, blank=True
    )
    user_agent_info = models.CharField(max_length=255)

    class Meta:
        verbose_name = "user_login_activity"
        verbose_name_plural = "user_login_activities"

        ordering = ["-login_datetime"]
