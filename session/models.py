from django.db import models


class Session(models.Model):
    session_key = models.CharField(max_length=256, unique=True)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
