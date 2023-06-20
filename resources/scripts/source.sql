DROP VIEW IF EXISTS "Wärmeerzeuger/Netzpumpe" CASCADE;
CREATE VIEW "Wärmeerzeuger/Netzpumpe" AS
SELECT point."type"        AS "Typ",
       pipe."massFlowRate" AS "Massenstrom (kg/s)",
       ddn."Druckverlust des kritischen Pfads (bar)",
       ddn."spez. Druckverlust des kritischen Pfads (Pa/m)",
       edq."Jährlicher Energiebedarf Heizung netto (MWh)",
       edq."Jährlicher Energiebedarf Warmwasser netto (MWh)",
       edq."Jährlicher Gesamtenergiebedarf netto (MWh)",
       edq."Jährlicher Energieverlust Netz (MWh)",
       edq."Anteil Energieverlust Netz (%)",
       edq."Jährlicher Gesamtenergiebedarf brutto (MWh)",

       ldq."Leistungsbedarf Heizung netto (kW)",
       ldq."Gleichzeitigkeit Heizung [20%] (kW)",
       ldq."Leistungsbedarf Heizung netto [80%] (kW)",
       ldq."Leistungsverlust Netz Winter (kW)",
       ldq."Anteil Leistungsverlust Netz Winter (%)",
       ldq."Gesamtleistungsbedarf Winter (kW)",

       ldq."Leistungsbedarf Warmwasser netto (kW)",
       ldq."Gleichzeitigkeit Warmwasser [20%] (kW)",
       ldq."Leistungsbedarf Warmwasser netto [80%] (kW)",
       ldq."Leistungsverlust Netz Sommer (kW)",
       ldq."Anteil Leistungsverlust Netz Sommer (%)",
       ldq."Gesamtleistungsbedarf Sommer (kW)",

       point."geometry"
FROM point
         JOIN pipe
              ON point."id" = pipe."startPointId" OR
                 point."id" = pipe."endPointId",
     "Druckverlust des Netzes" ddn,
     "Energiebedarf des Quartiers" edq,
     "Leistungsbedarf des Quartiers" ldq
WHERE "type" = 'Source';