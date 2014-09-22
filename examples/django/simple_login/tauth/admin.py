from django.contrib import admin
from models import Role

class RoleAdmin(admin.ModelAdmin):
    list_display = ('uri', )

admin.site.register(Role, RoleAdmin)

