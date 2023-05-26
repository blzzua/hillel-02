# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator


User = get_user_model()


class Feedback(models.Model):
    name = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    response = models.TextField()
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.response[:50]}'

    def rating_as_stars(self):
        if isinstance(self.rating, int):
            num = max(1, min(5, int(self.rating)))
            return "⭐" * num
        else:
            return "⚝"
