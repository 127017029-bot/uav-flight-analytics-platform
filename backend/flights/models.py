from django.db import models
from drones.models import Drone

class Flight(models.Model):
    drone = models.ForeignKey(
        Drone,
        on_delete=models.CASCADE
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    distance = models.FloatField(default=0)
    max_altitude = models.FloatField(default=0)

    def __str__(self):
        return f"Flight {self.id}"