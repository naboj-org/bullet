from django.contrib import admin
from documents import models


@admin.register(models.CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "branch")
    list_filter = ("branch",)
