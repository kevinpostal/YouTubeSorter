from django.contrib import admin
from .models import Credentials

class CredentialsAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at','updated_at')


admin.site.register(Credentials, CredentialsAdmin)