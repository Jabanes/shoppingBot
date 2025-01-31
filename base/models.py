from django.db import models
from django.contrib.auth.models import User  # To connect the user model

class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    item = models.CharField(max_length=255)
    quantity = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item} ({self.quantity}) by {self.user.username} on {self.date_added}"
