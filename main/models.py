from django.db import models
class Book(models.Model):
    name = models.CharField(max_length=255)
    date_added = models.DateField(auto_now_add=True)
    page = models.IntegerField()
    description = models.TextField()# Create your models here.
