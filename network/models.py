from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # username = models.CharField(max_length=25)
    image = models.CharField(max_length=250)
    following = models.ManyToManyField(User, symmetrical=False, blank=True, related_name="follower")


    def __str__(self):
        return self.user.username

# Create Profile when User is created
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# Posts
class Post(models.Model):
    body = models.CharField(max_length=250)
    post_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, symmetrical=False, default=0, related_name="likes")

    def __str__(self):
        return self.body
