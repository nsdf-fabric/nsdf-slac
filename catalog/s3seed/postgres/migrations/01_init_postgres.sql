DROP TABLE IF EXISTS catalog;

CREATE TABLE catalog (
    catalog VARCHAR NOT NULL,
    bucket VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    size BIGINT NOT NULL,
    last_modified VARCHAR NULL,
    etag VARCHAR NULL,
    inserted_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    ext VARCHAR GENERATED ALWAYS AS (
        CASE
            WHEN length(split_part(name, '.', -1)) <= 6 THEN split_part(name, '.', -1)
            ELSE ''
        END
    ) STORED,
    PRIMARY KEY (catalog, bucket, name)
);

CREATE INDEX idx_catalog_bucket ON catalog (catalog, bucket);
