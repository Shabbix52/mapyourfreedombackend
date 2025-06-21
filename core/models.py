from django.db import models

# Only keep your Book model here

class Book(models.Model):
    name = models.CharField(max_length=256)
    price = models.IntegerField()
    language = models.CharField(max_length=256)
    path = models.FileField(max_length=1000)

    def __str__(self):
        return f"{self.name}"
