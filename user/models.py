from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    session = models.ForeignKey("Group",
                                 on_delete=models.SET_NULL,
                                 null=True)
    is_manager = models.BooleanField(default=False)
    
    def __str__(self):
        return self.first_name+' '+self.last_name
    
class Group(models.Model):
    owner = models.ForeignKey(CustomUser,
                              on_delete=models.SET_NULL,
                              null=True,
                              related_name='group_owner')
    password = models.CharField(max_length=50)
    