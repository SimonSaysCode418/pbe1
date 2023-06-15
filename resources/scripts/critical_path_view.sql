DROP VIEW IF EXISTS "Kritischer Pfad";
CREATE VIEW "Kritischer Pfad"
AS
SELECT *
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