from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

# Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=25)
    image = models.CharField(max_length=250)

    def __str__(self):
        return self.username
        
# Posts
class Post(models.Model):
    body = models.CharField(max_length=250)
    post_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.body