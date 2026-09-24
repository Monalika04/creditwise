CREATE SCHEMA raw;

CREATE SCHEMA staging;

CREATE SCHEMA warehouse;

CREATE SCHEMA analytics;



SELECT schema_name
FROM information_schema.schemata
WHERE schema_name IN (
    'raw',
    'staging',
    'warehouse',
    'analytics'
)
ORDER BY schema_name;