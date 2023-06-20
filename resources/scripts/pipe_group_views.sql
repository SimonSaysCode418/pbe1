DROP VIEW IF EXISTS "Agg. Rohrdaten" CASCADE;
CREATE VIEW "Agg. Rohrdaten" AS
SELECT CASE
           WHEN GROUPING("location") = 1
               THEN 'Gesamt'
           ELSE "location"
           END                          AS "Rohrart",
       SUM("costsFlow")                 AS "Kosten VL (€)",
       SUM("costsReturn")               AS "Kosten RL (€)",
       SUM("costsFlow" + "costsReturn") AS "Kosten (€)"
FROM pipe
GROUP BY
    ROLLUP ("location")
ORDER BY "location" <> 'Gesamt', "location";

SELECT *
FROM "Agg. Rohrdaten";