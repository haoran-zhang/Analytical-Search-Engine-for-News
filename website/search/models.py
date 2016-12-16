from django.db import models

# Create your models here.
class possible_entity(models.Model):
    entity=models.CharField(max_length=20)

class Article(models.Model):
    title = models.CharField(max_length=200)
    url=models.CharField(max_length=200)

