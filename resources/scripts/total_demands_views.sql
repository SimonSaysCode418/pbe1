DROP VIEW IF EXISTS "Energiebedarf des Quartiers" CASCADE;
CREATE VIEW "Energiebedarf des Quartiers" AS
SELECT ROUND(SUM("demandHeating") / 1000000.0, 2)              AS "Jährlicher Energiebedarf Heizung netto (MWh)",
       ROUND(SUM("demandHeating") / 0.9 * 0.1 / 1000000.0, 2)  AS "Jährlicher Wärmeverlust Heizung (MWh)",
       ROUND(SUM("demandHeating") / 0.9 / 1000000.0, 2)        AS "Jährlicher Energiebedarf Heizung brutto (MWh)",
       ROUND(SUM("demandHotWater") / 1000000.0, 2)             AS "Jährlicher Energiebedarf Warmwasser netto (MWh)",
       ROUND(SUM("demandHotWater") / 0.9 * 0.1 / 1000000.0, 2) AS "Jährlicher Wärmeverlust Warmwasser (MWh)",
       ROUND(SUM("demandHotWater") / 0.9 / 1000000.00, 2)      AS "Jährlicher Energiebedarf Warmwasser brutto (MWh)"
FROM building;

-- TODO: Netzwärmebedarf ergänzen!!
DROP VIEW IF EXISTS "Leistungsbedarf des Quartiers" CASCADE;
CREATE VIEW "Leistungsbedarf des Quartiers" AS
SELECT ROUND(SUM("powerHeating") / 1000.0, 2)        AS "Leistungsbedarf Heizung netto (kW)",
       ROUND(SUM("powerHeating") * 0.2 / 1000.0, 2)  AS "Gleichzeitigkeit Heizung (kW)",
       ROUND(SUM("powerHeating") * 0.8 / 1000.0, 2)  AS "Leistungsbedarf Heizung netto [80%] (kW)",
       ROUND(SUM("powerHotWater") / 1000.0, 2)       AS "Leistungsbedarf Warmwasser netto (kW)",
       ROUND(SUM("powerHotWater") * 0.2 / 1000.0, 2) AS "Gleichzeitigkeit Warmwasser (kW)",
       ROUND(SUM("powerHotWater") * 0.8 / 1000.0, 2) AS "Leistungsbedarf Warmwasser netto [80%] (kW)"
FROM building;

DROP VIEW IF EXISTS "Volllaststunden des Quartiers";
CREATE VIEW "Volllaststunden des Quartiers" AS
SELECT "Jährlicher Energiebedarf Heizung netto (MWh)",
       "Leistungsbedarf Heizung netto (kW)",
       "Jährlicher Energiebedarf Warmwasser netto (MWh)",
       "Leistungsbedarf Warmwasser netto (kW)",
       ROUND("Jährlicher Energiebedarf Heizung netto (MWh)" * 1000.0 / "Leistungsbedarf Heizung netto (kW)")
           AS "Volllaststunden Heizung",
       ROUND("Jährlicher Energiebedarf Warmwasser netto (MWh)" * 1000.0 / "Leistungsbedarf Warmwasser netto (kW)")
           AS "Volllaststunden Warmwasser"
FROM "Energiebedarf des Quartiers",
     "Leistungsbedarf des Quartiers";