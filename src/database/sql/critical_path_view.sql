DROP VIEW IF EXISTS public.critical_path;
CREATE VIEW public.critical_path
AS
SELECT *
FROM (SELECT pc."pathId"
      FROM public.shortest_path_connector AS pc
      WHERE pc."pointId" = (SELECT spc."pointId"
                            FROM (SELECT "pointId", SUM(p.length) AS "length"
                                  FROM public.shortest_path_connector AS spc
                                           JOIN pipe_path AS p ON spc."pathId" = p.id
                                  GROUP BY "pointId") AS spc
                            GROUP BY spc."pointId"
                            ORDER BY MAX(spc."length") DESC
                            LIMIT 1)) AS cpi
         JOIN pipe_path pp
              ON cpi."pathId" = pp.id;