"""User models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.users.models import User, UserLoginActivity



class CustomUserAdmin(UserAdmin):
    """User model admin."""

    fieldsets = UserAdmin.fieldsets + ((None,
                                        {
                                            "fields":
                                            ("is_verified", "stripe_customer_id", "stripe_plan_customer_id", "net_income",
                                             "withdrawn", "used_for_purchases", "available_for_withdrawal",
                                             "pending_clearance", "active_month", "have_active_plan", "is_free_trial",
                                             "passed_free_trial_once", "currency", "plan_default_payment_method",
                                             "is_online", "paypal_email")}),)

    list_display = ("email", "first_name", "last_name", "is_staff",
                    "is_client", "is_online")
    list_filter = (
        "is_client",
        "is_staff",
        "created",
        "modified",
        "is_online"
    )



@admin.register(UserLoginActivity)
class UserLoginActivityAdmin(admin.ModelAdmin):
    """UserLoginActivity model admin."""
    list_display = ("login_username", "created")


admin.site.register(User, CustomUserAdmin)
