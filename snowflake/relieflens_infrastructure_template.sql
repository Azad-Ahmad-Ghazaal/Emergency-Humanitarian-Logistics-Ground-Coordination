-- ReliefLens / Snowflake CoCo SQL starter
-- TEMPLATE ONLY: replace identifiers after inspecting the actual Marketplace schema.
-- Do not execute unchanged. CoCo should adapt this to verified provider tables.
--
-- Expected logical inputs:
--   RELIEFLENS_INCIDENTS: incident_id, location_name, latitude, longitude, priority, created_at
--   PUBLIC_INFRASTRUCTURE: feature_id, feature_type, feature_name, latitude, longitude,
--                          source_name, source_updated_at
--
-- Coordinates must use the same CRS (WGS84 decimal degrees) before distance calculation.
-- This query measures proximity only; it does NOT assess structural safety/passability.

SELECT
    i.incident_id,
    i.location_name AS incident_location,
    i.priority,
    infra.feature_id,
    infra.feature_type,
    infra.feature_name,
    ST_DISTANCE(
        ST_MAKEPOINT(i.longitude, i.latitude),
        ST_MAKEPOINT(infra.longitude, infra.latitude)
    ) AS distance_meters,
    infra.source_name,
    infra.source_updated_at
FROM RELIEFLENS_INCIDENTS AS i
LEFT JOIN PUBLIC_INFRASTRUCTURE AS infra
    ON ST_DISTANCE(
        ST_MAKEPOINT(i.longitude, i.latitude),
        ST_MAKEPOINT(infra.longitude, infra.latitude)
    ) <= 5000
WHERE i.latitude IS NOT NULL
  AND i.longitude IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY i.incident_id
    ORDER BY distance_meters NULLS LAST
) = 1
ORDER BY
    CASE i.priority
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        ELSE 4
    END,
    distance_meters;
