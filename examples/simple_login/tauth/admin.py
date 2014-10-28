from django.contrib import admin
import models

class RoleAdmin(admin.ModelAdmin):
    list_display = ('uri', )

admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.Permission)
admin.site.register(models.Resource)

