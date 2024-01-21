from django.contrib import admin

from documents import models


class SelfServeCertificateInline(admin.TabularInline):
    model = models.SelfServeCertificate
    autocomplete_fields = ("venue",)


@admin.register(models.CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "branch")
    list_filter = ("branch",)
    inlines = (SelfServeCertificateInline,)
