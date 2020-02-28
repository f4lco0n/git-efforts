from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Repository(models.Model):
    url = models.CharField(max_length=250, unique=False)
    user = models.ForeignKey(User,related_name='user',on_delete=models.CASCADE,default='')

    repositorys = models.ManyToManyField(User,related_name='users')

    class Meta:
        unique_together = [['url', 'user']]

    def __str__(self):
        return self.url