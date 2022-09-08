from bullet_admin.models import BranchRole
from django.contrib import admin


@admin.register(BranchRole)
class BranchRoleAdmin(admin.ModelAdmin):
    list_display = ("branch", "user", "role", "can_translate", "can_delegate")
    list_filter = ("branch", "role")
    autocomplete_fields = ("user",)
