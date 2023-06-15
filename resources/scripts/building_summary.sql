DROP VIEW IF EXISTS heat_demand;
CREATE VIEW heat_demand
AS SELECT
	ROUND(SUM("Wärmebedarf Heizung (kWh/a)"+"Wärmebedarf Warmwasser (kWh/a)") / 1000.0) AS "Jährlicher Energiebedarf (MWh)",
	ROUND(SUM("Wärmebedarf Heizung (kWh/a)"+"Wärmebedarf Warmwasser (kWh/a)") / 0.9 * 0.1 / 1000.0) AS "Jährlicher Wärmeverlust (MWh)",
	ROUND(SUM("Wärmebedarf Heizung (kWh/a)"+"Wärmebedarf Warmwasser (kWh/a)") / 0.9 / 1000.0) AS "Jährlicher Energiebedarf brutto (MWh)",
	ROUND(SUM("Wärmebedarf Warmwasser (kWh/a)") / 1000.0) AS "Jährlicher Energiebedarf Sommer nur WW (MWh)",
	ROUND(SUM("Wärmebedarf Warmwasser (kWh/a)") / 0.9 * 0.1 / 1000.0) AS "Jährlicher Wärmeverlust Sommer nur WW (MWh)",
	ROUND(SUM("Wärmebedarf Warmwasser (kWh/a)") / 0.9 / 1000.00) AS "Jährlicher Energiebedarf brutto Sommer nur WW (MWh)"
FROM PUBLIC.building_data;

DROP TABLE IF EXISTS heating_power_demand;
CREATE TABLE heating_power_demand
AS SELECT
	ROUND(SUM("Leistungsbedarf Heizung (W)") / 1000.0) AS "Leistungsbedarf netto (kW)",
	ROUND(SUM("Leistungsbedarf Heizung (W)") * 0.2 / 1000.0) AS "Gleichzeitigkeit (kW)",
	ROUND(SUM("Leistungsbedarf Heizung (W)") * 0.8 / 1000.0) AS "Leistungsbedarf netto [80%] (kW)",
	ROUND(SUM("Leistungsbedarf Warmwasser (W)") / 1000.0) AS "Leistungsbedarf netto Sommer nur WW (kW)",
	ROUND(SUM("Leistungsbedarf Warmwasser (W)") * 0.2 / 1000.0) AS "Gleichzeitigkeit Sommer nur WW (kW)",
	ROUND(SUM("Leistungsbedarf Warmwasser (W)") * 0.8 / 1000.0) AS "Leistungsbedarf netto [80%] Sommer nur WW (kW)"
FROM public.building_data
WHERE NOT "Gebäudetyp"='Seminar';

ALTER TABLE heating_power_demand ADD COLUMN "Leistungsverluste Netz (kW)" NUMERIC;
UPDATE heating_power_demand
SET "Leistungsverluste Netz (kW)"=ROUND(("Jährlicher Wärmeverlust (MWh)" * 1000) / 8760)
FROM heat_demand
CROSS JOIN public.building_data;

ALTER TABLE heating_power_demand ADD COLUMN "Leistungsbedarf brutto (kW)" NUMERIC;
UPDATE heating_power_demand
SET "Leistungsbedarf brutto (kW)"="Leistungsbedarf netto [80%] (kW)"+"Leistungsverluste Netz (kW)"
WHERE true;

SELECT ROUND(heat_demand."Jährlicher Energiebedarf brutto (MWh)" * 1000.0 / heating_power_demand."Leistungsbedarf brutto (kW)")
AS "Volllaststunden"
FROM heating_power_demand, heat_demand; -- soll zwischen 1300 und 2000 liegen --> Abgleichen mit Werten aus Kurs

SELECT "Straße", "Hausnummer", "Gebäudetyp", ROUND("Wärmebedarf Heizung (kWh/a)"* 1000.0 / "Leistungsbedarf Heizung (W)")
	FROM building_data;

SELECT * FROM building_data;