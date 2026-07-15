from django.db import models


class Session(models.Model):
    session_key = models.CharField(max_length=256, unique=True)
    user_id = models.IntegerField(null=True, blank=True)
    session_data = models.TextField()
    expire_date = models.DateTimeField()


    def __str__(self):
        return self.session_key