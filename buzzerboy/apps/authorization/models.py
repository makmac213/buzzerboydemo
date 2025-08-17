
from django.contrib.auth.models import User
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'authorization_companies'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name
    

class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name="profiles", on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name="companies",
                                    on_delete=models.SET_NULL, null=True)
    is_default = models.BooleanField(default=False)
    default_language = models.CharField(max_length=7, default="en")

    class Meta:
        db_table = 'authorization_user_profiles'
