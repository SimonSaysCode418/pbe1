DROP VIEW IF EXISTS "Kritischer Pfad" CASCADE;
CREATE VIEW "Kritischer Pfad"
AS
SELECT r.*
FROM (SELECT pc."pipeId"
      FROM shortest_path_connector AS pc
      WHERE pc."pointId" = (SELECT spc."pointId"
                            FROM (SELECT "pointId", SUM(p.length) AS "length"
                                  FROM shortest_path_connector AS spc
                                           JOIN pipe AS p ON spc."pipeId" = p.id
                                  GROUP BY "pointId") AS spc
                            GROUP BY spc."pointId"
                            ORDER BY MAX(spc."length") DESC
                            LIMIT 1)) AS cpi
         JOIN "Rohrleitungen" r
              ON cpi."pipeId" = r."ID";

-- DROP VIEW IF EXISTS "Druckverlust des Netzes";
-- CREATE VIEW "Druckverlust des Netzes" AS
SELECT ROUND((SUM("Druckverlust VL (Pa)") + SUM("Druckverlust RL (Pa)") + 100000) / 100000, 2)
           AS "Druckverlust des kritischen Pfads (bar)",
       ROUND((SUM("Druckverlust VL (Pa)") + SUM("Druckverlust RL (Pa)")) / SUM("Länge (m)" * 2), 2)
           AS "spez. Druckverlust des kritischen Pfads (Pa/m)"
FROM "Kritischer Pfad";

SELECT *
FROM "Kritischer Pfad";