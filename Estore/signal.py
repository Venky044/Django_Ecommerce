
from django.contrib.auth.models import User
from .models import Customer

from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver

def createCustomer(sender, instance, created, **kwargs):
    if created:
        user = instance
        customer = Customer.objects.create(
            user = user,
            username = user.username,
            name = user.first_name,
            email = user.email,
        )

post_save.connect(createCustomer, sender=User)


def deleteUser(sender, instance, **kwargs):
    user = instance.user
    user.delete()

post_delete.connect(deleteUser, sender=Customer)