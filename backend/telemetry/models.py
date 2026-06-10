from django.db import models
from flights.models import Flight

class Telemetry(models.Model):
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE
    )

    timestamp = models.DateTimeField()

    latitude = models.FloatField()
    longitude = models.FloatField()

    altitude = models.FloatField()
    speed = models.FloatField()

    battery = models.FloatField()
    motor_rpm = models.FloatField()

    def __str__(self):
        return f"Telemetry {self.id}"
