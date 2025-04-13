from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    saved_cities = models.ManyToManyField('City')

    def __str__(self):
        return self.user.username

class City(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True,  # Allow null temporarily for migration
        default=1   # Default to user ID 1 (usually the superuser)
    )
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['name', 'user']
        verbose_name_plural = 'cities'

    def __str__(self):
        return f"{self.name} - {self.user.username}"