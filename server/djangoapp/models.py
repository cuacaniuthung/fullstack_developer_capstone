from django.db import models
from django.utils.timezone import now


# Define Car Make model
class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


# Define Car Model model
class CarModel(models.Model):
    # Many-to-One relationship
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
        ('BMW', 'bmw'),
        ('Toyota', 'toyota'),
        ('Peugeot', 'peugeot')
    ]
    type = models.CharField(max_length=10, choices=CAR_TYPES, default='SUV')
    year = models.IntegerField(default=2023)  # Giả sử trường year đã được sửa để không còn lỗi W291/E302

    def __str__(self):
        return f"{self.car_make.name} - {self.name} ({self.type})"
