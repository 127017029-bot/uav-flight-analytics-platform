from django.db import models


class TelemetryData(models.Model):
    """High-frequency telemetry data point from a drone during flight.

    Each record represents a single sensor snapshot captured at a specific
    timestamp during a flight sortie.  Fields cover position, attitude,
    battery, motors, vibration, GPS quality, environmental conditions,
    and anomaly flags.
    """

    # --- Relationships ---
    flight = models.ForeignKey(
        'flights.Flight', related_name='telemetry_data',
        on_delete=models.CASCADE,
    )

    # --- Timing ---
    timestamp = models.DateTimeField(db_index=True)
    sequence_number = models.IntegerField(default=0)

    # --- Position ---
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude_msl = models.FloatField(null=True, blank=True, help_text='Altitude above mean sea level (m)')
    altitude_agl = models.FloatField(null=True, blank=True, help_text='Altitude above ground level (m)')

    # --- Velocity ---
    ground_speed = models.FloatField(default=0, help_text='Ground speed (m/s)')
    air_speed = models.FloatField(default=0, help_text='Air speed (m/s)')
    vertical_speed = models.FloatField(default=0, help_text='Vertical speed (m/s)')

    # --- Attitude ---
    heading = models.FloatField(default=0, help_text='Heading in degrees')
    roll = models.FloatField(default=0, help_text='Roll angle in degrees')
    pitch = models.FloatField(default=0, help_text='Pitch angle in degrees')
    yaw = models.FloatField(default=0, help_text='Yaw angle in degrees')

    # --- Battery ---
    battery_voltage = models.FloatField(null=True, blank=True)
    battery_current = models.FloatField(null=True, blank=True)
    battery_percentage = models.FloatField(null=True, blank=True)
    battery_temperature = models.FloatField(null=True, blank=True)

    # --- Motors ---
    motor_rpm_1 = models.FloatField(null=True, blank=True)
    motor_rpm_2 = models.FloatField(null=True, blank=True)
    motor_rpm_3 = models.FloatField(null=True, blank=True)
    motor_rpm_4 = models.FloatField(null=True, blank=True)
    motor_temp_1 = models.FloatField(null=True, blank=True)
    motor_temp_2 = models.FloatField(null=True, blank=True)
    motor_temp_3 = models.FloatField(null=True, blank=True)
    motor_temp_4 = models.FloatField(null=True, blank=True)

    # --- Vibration ---
    vibration_x = models.FloatField(null=True, blank=True)
    vibration_y = models.FloatField(null=True, blank=True)
    vibration_z = models.FloatField(null=True, blank=True)

    # --- GPS Quality ---
    gps_satellites = models.IntegerField(null=True, blank=True)
    gps_fix_type = models.IntegerField(null=True, blank=True)
    gps_hdop = models.FloatField(null=True, blank=True)

    # --- Communications ---
    signal_strength = models.FloatField(null=True, blank=True)

    # --- Environmental ---
    wind_speed_est = models.FloatField(null=True, blank=True)
    wind_direction_est = models.FloatField(null=True, blank=True)
    ambient_temperature = models.FloatField(null=True, blank=True)
    barometric_pressure = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)

    # --- Anomaly Detection ---
    is_anomaly = models.BooleanField(default=False)
    anomaly_score = models.FloatField(null=True, blank=True)

    # --- Metadata ---
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Telemetry Data'
        verbose_name_plural = 'Telemetry Data'
        indexes = [
            models.Index(fields=['flight', 'timestamp'], name='idx_telem_flight_ts'),
        ]

    def __str__(self):
        return f"Telemetry #{self.sequence_number} @ {self.timestamp}"
