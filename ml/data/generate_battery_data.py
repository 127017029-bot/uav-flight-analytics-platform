"""
Synthetic Battery Degradation Data Generator
=============================================
Generates realistic LiPo battery charge-discharge cycle data
for training the Battery RUL (Remaining Useful Life) LSTM model.

Based on empirical degradation curves from NASA PCoE Battery Dataset
patterns with added stochastic variability.

Output: CSV with per-cycle features suitable for time-series modeling.
"""

import numpy as np
import pandas as pd
import os
import argparse
from datetime import datetime


def generate_battery_degradation_data(
    num_batteries: int = 20,
    max_cycles: int = 500,
    output_dir: str = None,
) -> pd.DataFrame:
    """
    Generate synthetic battery degradation dataset.

    Each battery undergoes charge-discharge cycles with gradually
    decreasing capacity following an empirical degradation model:
    C(n) = C0 * (1 - α * n^β) + noise

    Args:
        num_batteries: Number of synthetic batteries to simulate
        max_cycles: Maximum charge-discharge cycles per battery
        output_dir: Directory to save CSV output

    Returns:
        DataFrame with per-cycle battery features
    """
    all_records = []

    for battery_id in range(1, num_batteries + 1):
        # Randomize battery characteristics
        initial_capacity = np.random.uniform(4800, 5200)  # mAh
        alpha = np.random.uniform(0.0003, 0.0008)  # degradation rate
        beta = np.random.uniform(0.85, 1.15)  # degradation exponent
        internal_resistance_base = np.random.uniform(0.012, 0.020)  # Ohms
        temp_sensitivity = np.random.uniform(0.8, 1.2)

        # End-of-life threshold (80% of initial capacity)
        eol_capacity = initial_capacity * 0.80
        actual_rul = max_cycles  # will be computed

        for cycle in range(1, max_cycles + 1):
            # Capacity degradation model (empirical curve)
            capacity = initial_capacity * (1 - alpha * cycle ** beta)
            capacity += np.random.normal(0, initial_capacity * 0.005)
            capacity = max(capacity, initial_capacity * 0.5)

            # State of Health
            soh = (capacity / initial_capacity) * 100

            # Internal resistance increases with degradation
            ir_growth = internal_resistance_base * (1 + 0.002 * cycle ** 0.9)
            internal_resistance = ir_growth + np.random.normal(0, 0.001)

            # Voltage characteristics
            voltage_max = 4.2 - 0.0001 * cycle + np.random.normal(0, 0.01)
            voltage_min = 3.0 + 0.0002 * cycle + np.random.normal(0, 0.015)
            voltage_mean = (voltage_max + voltage_min) / 2 + np.random.normal(0, 0.02)
            voltage_std = np.random.uniform(0.15, 0.35)

            # Current characteristics (varies with usage pattern)
            current_mean = np.random.uniform(8, 18)
            current_std = np.random.uniform(2, 6)
            current_max = current_mean + current_std * 2.5

            # Temperature characteristics
            base_temp = 25 + temp_sensitivity * (current_mean / 10) * 8
            temp_mean = base_temp + 0.01 * cycle + np.random.normal(0, 1.5)
            temp_max = temp_mean + np.random.uniform(5, 15)
            temp_std = np.random.uniform(1.5, 4)

            # Charge/discharge duration (increases as battery ages)
            charge_duration = 45 + 0.03 * cycle + np.random.normal(0, 2)
            discharge_duration = 28 - 0.02 * cycle + np.random.normal(0, 1.5)
            discharge_duration = max(discharge_duration, 10)

            # Energy metrics
            energy_charged = capacity * voltage_mean / 1000  # Wh
            energy_discharged = energy_charged * np.random.uniform(0.88, 0.96)
            coulombic_efficiency = energy_discharged / energy_charged * 100

            # Degradation rate (capacity loss per cycle, rolling)
            if cycle > 10:
                prev_cap = initial_capacity * (1 - alpha * (cycle - 10) ** beta)
                degradation_rate = (prev_cap - capacity) / 10
            else:
                degradation_rate = alpha * initial_capacity * 0.01

            # RUL computation
            remaining_capacity_margin = capacity - eol_capacity
            if remaining_capacity_margin <= 0:
                rul = 0
            else:
                # Estimate cycles until EOL
                rul = max(0, int(remaining_capacity_margin / max(degradation_rate, 0.1)))
                rul = min(rul, max_cycles - cycle)

            record = {
                'battery_id': battery_id,
                'cycle': cycle,
                'capacity_measured': round(capacity, 2),
                'initial_capacity': round(initial_capacity, 2),
                'state_of_health': round(soh, 2),
                'internal_resistance': round(internal_resistance, 4),
                'voltage_max': round(voltage_max, 3),
                'voltage_min': round(voltage_min, 3),
                'voltage_mean': round(voltage_mean, 3),
                'voltage_std': round(voltage_std, 3),
                'current_mean': round(current_mean, 2),
                'current_std': round(current_std, 2),
                'current_max': round(current_max, 2),
                'temperature_mean': round(temp_mean, 1),
                'temperature_max': round(temp_max, 1),
                'temperature_std': round(temp_std, 2),
                'charge_duration_min': round(charge_duration, 1),
                'discharge_duration_min': round(discharge_duration, 1),
                'energy_charged_wh': round(energy_charged, 2),
                'energy_discharged_wh': round(energy_discharged, 2),
                'coulombic_efficiency': round(coulombic_efficiency, 2),
                'degradation_rate': round(degradation_rate, 4),
                'remaining_useful_life': rul,
            }
            all_records.append(record)

            # Stop if battery is dead
            if soh < 50:
                break

    df = pd.DataFrame(all_records)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, 'battery_degradation.csv')
        df.to_csv(filepath, index=False)
        print(f"[OK] Generated {len(df)} records for {num_batteries} batteries → {filepath}")

    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate synthetic battery data')
    parser.add_argument('--batteries', type=int, default=20, help='Number of batteries')
    parser.add_argument('--cycles', type=int, default=500, help='Max cycles per battery')
    parser.add_argument('--output', default='ml/data', help='Output directory')
    args = parser.parse_args()

    generate_battery_degradation_data(args.batteries, args.cycles, args.output)
