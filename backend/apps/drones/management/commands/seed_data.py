"""
Database Seed Command
=====================
Populates the database with realistic demo data for all models.
Useful for development, demos, and testing.

Usage: python manage.py seed_data
"""

import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.drones.models import Drone, ComponentHealth, BatteryProfile
from apps.accounts.models import User, Pilot
from apps.flights.models import Flight, FlightAnalytics
from apps.missions.models import Mission, Waypoint
from apps.maintenance.models import MaintenanceRecord
from apps.alerts.models import Alert


MANUFACTURERS = ['DJI', 'Autel', 'Skydio', 'Parrot', 'Yuneec']
DRONE_MODELS = {
    'DJI': ['Matrice 350 RTK', 'Mavic 3 Enterprise', 'Phantom 4 RTK', 'Inspire 3'],
    'Autel': ['EVO II Pro', 'Dragonfish', 'Alpha'],
    'Skydio': ['X10', 'S2+'],
    'Parrot': ['ANAFI Ai', 'ANAFI USA'],
    'Yuneec': ['H520E', 'H850'],
}
DRONE_NAMES = [
    'Eagle-1', 'Falcon-2', 'Hawk-3', 'Osprey-4', 'Phoenix-5',
    'Condor-6', 'Raptor-7', 'Sparrow-8', 'Viper-9', 'Storm-10',
    'Atlas-11', 'Titan-12',
]


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Alert.objects.all().delete()
            MaintenanceRecord.objects.all().delete()
            Waypoint.objects.all().delete()
            Mission.objects.all().delete()
            FlightAnalytics.objects.all().delete()
            Flight.objects.all().delete()
            BatteryProfile.objects.all().delete()
            ComponentHealth.objects.all().delete()
            Drone.objects.all().delete()
            Pilot.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self._create_users()
        self._create_drones()
        self._create_flights()
        self._create_missions()
        self._create_maintenance()
        self._create_alerts()
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))

    def _create_users(self):
        self.stdout.write('Creating users and pilots...')
        roles = ['fleet_manager', 'pilot', 'pilot', 'pilot', 'analyst']
        self.users = []
        self.pilots = []

        for i, role in enumerate(roles, 1):
            user, created = User.objects.get_or_create(
                username=f'user{i}',
                defaults={
                    'email': f'user{i}@uavplatform.com',
                    'first_name': ['Arun', 'Priya', 'Vikram', 'Kavitha', 'Raj'][i-1],
                    'last_name': ['Kumar', 'Sharma', 'Singh', 'Nair', 'Patel'][i-1],
                    'role': role,
                    'organization': 'UAV Analytics Corp',
                }
            )
            if created:
                user.set_password('demo1234')
                user.save()
            self.users.append(user)

            if role == 'pilot':
                pilot, _ = Pilot.objects.get_or_create(
                    user=user,
                    defaults={
                        'license_number': f'UAV-{1000+i}',
                        'certification_level': random.choice(['basic', 'advanced', 'expert']),
                        'total_flight_hours': random.uniform(50, 500),
                        'rating': round(random.uniform(3.5, 5.0), 1),
                    }
                )
                self.pilots.append(pilot)

    def _create_drones(self):
        self.stdout.write('Creating drone fleet...')
        self.drones = []

        for i, name in enumerate(DRONE_NAMES):
            manufacturer = random.choice(MANUFACTURERS)
            model = random.choice(DRONE_MODELS[manufacturer])
            drone, created = Drone.objects.get_or_create(
                serial_number=f'SN-{10000+i}',
                defaults={
                    'name': name,
                    'model': model,
                    'manufacturer': manufacturer,
                    'drone_type': random.choice(['quadcopter', 'hexacopter', 'fixed_wing', 'vtol']),
                    'max_altitude_m': random.choice([120, 150, 200]),
                    'max_speed_ms': random.uniform(15, 30),
                    'max_flight_time_min': random.randint(25, 45),
                    'weight_kg': round(random.uniform(1.0, 5.0), 1),
                    'status': random.choices(
                        ['active', 'active', 'active', 'maintenance', 'offline'],
                        weights=[50, 30, 10, 7, 3]
                    )[0],
                    'total_flight_hours': round(random.uniform(10, 800), 1),
                    'total_flights': random.randint(20, 500),
                    'firmware_version': f'v{random.randint(3,5)}.{random.randint(0,9)}.{random.randint(0,9)}',
                    'last_maintenance_date': timezone.now() - timedelta(days=random.randint(5, 90)),
                    'next_maintenance_date': timezone.now() + timedelta(days=random.randint(5, 60)),
                }
            )
            self.drones.append(drone)

            if created:
                # Create component health records
                components = [
                    ('motor_1', 'Motor 1'), ('motor_2', 'Motor 2'),
                    ('motor_3', 'Motor 3'), ('motor_4', 'Motor 4'),
                    ('battery', 'Main Battery'), ('esc', 'ESC Board'),
                    ('gps', 'GPS Module'), ('imu', 'IMU Sensor'),
                    ('compass', 'Compass'), ('camera', 'Camera'),
                ]
                for comp_type, comp_name in components:
                    health = round(random.uniform(60, 100), 1)
                    status = 'healthy' if health > 80 else 'warning' if health > 50 else 'critical'
                    ComponentHealth.objects.create(
                        drone=drone,
                        component_type=comp_type,
                        component_name=comp_name,
                        health_score=health,
                        cycles_count=random.randint(50, 2000),
                        total_hours=round(random.uniform(10, 500), 1),
                        status=status,
                        degradation_rate=round(random.uniform(0, 0.05), 4),
                        predicted_rul_hours=round(random.uniform(50, 500), 1),
                    )

                # Create battery profile
                soh = round(random.uniform(70, 100), 1)
                BatteryProfile.objects.create(
                    drone=drone,
                    manufacturer=random.choice(['Tattu', 'Maxamps', manufacturer]),
                    chemistry='lipo',
                    cells_count=random.choice([4, 6]),
                    design_capacity_mah=random.choice([4500, 5000, 5200, 6000]),
                    current_capacity_mah=int(5000 * soh / 100),
                    voltage_nominal=round(random.choice([14.8, 22.2]), 1),
                    cycle_count=random.randint(50, 400),
                    state_of_health=soh,
                    estimated_rul_cycles=random.randint(50, 300),
                    degradation_rate_per_cycle=round(random.uniform(0.01, 0.08), 4),
                )

    def _create_flights(self):
        self.stdout.write('Creating flight records...')
        self.flights = []

        for i in range(30):
            drone = random.choice(self.drones)
            pilot = random.choice(self.pilots) if self.pilots else None
            start = timezone.now() - timedelta(days=random.randint(0, 60), hours=random.randint(0, 12))
            duration = random.randint(300, 2400)
            status = random.choice(['completed', 'completed', 'completed', 'aborted'])

            flight = Flight.objects.create(
                drone=drone,
                pilot=pilot,
                status=status,
                start_time=start,
                end_time=start + timedelta(seconds=duration),
                duration_seconds=duration,
                distance_km=round(random.uniform(0.5, 15), 2),
                max_altitude_m=round(random.uniform(30, 120), 1),
                avg_speed_ms=round(random.uniform(3, 15), 1),
                max_speed_ms=round(random.uniform(10, 25), 1),
                energy_consumed_wh=round(random.uniform(50, 200), 1),
                start_battery_pct=round(random.uniform(90, 100), 1),
                end_battery_pct=round(random.uniform(15, 45), 1),
                weather_condition=random.choice(['clear', 'cloudy', 'windy']),
                wind_speed_ms=round(random.uniform(0, 12), 1),
                temperature_c=round(random.uniform(18, 38), 1),
                risk_score=round(random.uniform(5, 60), 1),
                anomaly_count=random.randint(0, 5),
            )
            self.flights.append(flight)

            FlightAnalytics.objects.create(
                flight=flight,
                total_distance_m=flight.distance_km * 1000,
                max_altitude_m=flight.max_altitude_m,
                avg_speed_ms=flight.avg_speed_ms,
                max_speed_ms=flight.max_speed_ms,
                avg_vertical_speed_ms=round(random.uniform(0.5, 3), 1),
                energy_efficiency_m_per_wh=round(
                    flight.distance_km * 1000 / max(flight.energy_consumed_wh, 1), 2),
                flight_smoothness_score=round(random.uniform(70, 100), 1),
                path_efficiency=round(random.uniform(0.75, 1.0), 3),
                risk_score=flight.risk_score,
                anomaly_count=flight.anomaly_count,
                battery_consumed_pct=round(
                    flight.start_battery_pct - flight.end_battery_pct, 1),
                avg_motor_rpm=random.randint(4000, 6000),
                motor_rpm_variance=round(random.uniform(10, 200), 1),
                avg_vibration=round(random.uniform(0.2, 1.5), 3),
                max_vibration=round(random.uniform(1.0, 4.0), 3),
                gps_accuracy_avg_m=round(random.uniform(0.8, 2.5), 2),
            )

    def _create_missions(self):
        self.stdout.write('Creating missions...')
        mission_types = ['survey', 'inspection', 'delivery', 'surveillance', 'mapping']
        for i in range(8):
            mission = Mission.objects.create(
                name=f'Mission {["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"][i]}',
                description=f'Automated {random.choice(mission_types)} mission',
                mission_type=random.choice(mission_types),
                priority=random.choice(['low', 'medium', 'high']),
                status=random.choice(['completed', 'planned', 'draft', 'in_progress']),
                assigned_drone=random.choice(self.drones),
                estimated_distance_km=round(random.uniform(2, 20), 1),
                estimated_duration_min=random.randint(10, 60),
                max_altitude_m=random.choice([50, 80, 100, 120]),
                planned_start=timezone.now() + timedelta(days=random.randint(-30, 30)),
            )

            for j in range(random.randint(3, 8)):
                Waypoint.objects.create(
                    mission=mission,
                    sequence_order=j + 1,
                    latitude=10.79 + random.uniform(-0.01, 0.01),
                    longitude=78.70 + random.uniform(-0.01, 0.01),
                    altitude_m=random.uniform(30, 100),
                    speed_ms=random.uniform(5, 15),
                    action_type=random.choice(['flyover', 'hover', 'take_photo']),
                )

    def _create_maintenance(self):
        self.stdout.write('Creating maintenance records...')
        for i in range(15):
            MaintenanceRecord.objects.create(
                drone=random.choice(self.drones),
                maintenance_type=random.choice(['scheduled', 'predictive', 'corrective']),
                component=random.choice(['motor_1', 'battery', 'gps', 'camera', 'full_system']),
                title=f'Maintenance Record #{i+1}',
                description=f'Routine {random.choice(["inspection", "calibration", "replacement"])}',
                status=random.choice(['completed', 'pending', 'scheduled']),
                priority=random.choice(['low', 'medium', 'high']),
                scheduled_date=timezone.now() + timedelta(days=random.randint(-30, 30)),
                cost_estimate=round(random.uniform(50, 500), 2),
            )

    def _create_alerts(self):
        self.stdout.write('Creating alerts...')
        alert_configs = [
            ('battery_low', 'warning', 'Low Battery Warning', 'Battery at 18% - RTH recommended'),
            ('motor_anomaly', 'critical', 'Motor 3 Anomaly Detected', 'Vibration exceeds threshold by 2.3×'),
            ('temperature_warning', 'warning', 'Motor Temperature High', 'Motor 2 temp at 72°C'),
            ('maintenance_due', 'info', 'Scheduled Maintenance Due', 'Motor inspection due in 5 flight hours'),
            ('geofence_breach', 'critical', 'Geofence Breach', 'Drone exceeded operational boundary'),
            ('ai_prediction', 'warning', 'AI: Battery Degradation', 'Battery SoH trending below 80% in ~45 cycles'),
            ('gps_loss', 'critical', 'GPS Signal Degraded', 'Satellite count dropped to 4'),
        ]

        for alert_type, severity, title, message in alert_configs:
            Alert.objects.create(
                drone=random.choice(self.drones),
                flight=random.choice(self.flights) if self.flights else None,
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                ai_generated=alert_type == 'ai_prediction',
                confidence=round(random.uniform(0.7, 0.98), 2) if alert_type == 'ai_prediction' else None,
                resolved=random.choice([True, False]),
            )
