from django.contrib import admin

# Register your models here.
from .models import (
    Company,
    UserProfile
)


admin.site.register(Company)
admin.site.register(UserProfile)
