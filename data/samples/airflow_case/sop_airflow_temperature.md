# SOP: Airflow and Dryer Temperature Coupled Faults

## AIR-305 Fan Frequency Below Normal

Meaning: the fan inverter output frequency has dropped below the normal operating range, potentially reducing airflow through the dryer section.

Recommended checks:

1. Check fan inverter cooling module and heat sink condition.
2. Inspect airflow filter for blockage or contamination.
3. Verify fan inverter parameter settings and power supply stability.
4. Check for recent power fluctuations or voltage sags.
5. If frequency does not recover, switch to controlled stop and inspect fan motor and inverter.

Safety note: do not operate dryer with insufficient airflow – risk of overheating and solvent accumulation.

## DRY-122 Dryer Zone Temperature Deviation

Meaning: the measured dryer zone temperature is outside the control band for more than 90 seconds.

Recommended checks:

1. Confirm the recipe target temperature and upper/lower control limits.
2. Check temperature sensor wiring and calibration status.
3. Inspect heater relay response and controller output.
4. Check fan frequency stability and airflow blockage.
5. If deviation persists, switch to controlled stop and inspect heater module.

Safety note: do not bypass temperature interlocks.

## DRY-110 Dryer Zone 1 Temperature Approaching Limit

Meaning: dryer zone 1 temperature is approaching the upper control limit but has not yet exceeded it.

Recommended checks:

1. Monitor zone 1 temperature trend and compare with zone 2.
2. Check if fan frequency drop is affecting airflow uniformity.
3. Verify zone 1 heater controller is responding correctly.

## QCS-318 Thickness Drift

Meaning: inline inspection detected coating thickness drifting away from target band.

Recommended checks:

1. Correlate drift time with temperature, tension and line speed changes.
2. Isolate affected material roll range.
3. Request quality engineer review before release.
