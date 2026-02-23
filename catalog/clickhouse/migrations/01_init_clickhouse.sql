DROP DATABASE IF EXISTS nsdf;

CREATE DATABASE IF NOT EXISTS nsdf;

-- https://github.com/ClickHouse/ClickHouse/issues/14634 (3 stands for 10^-3==milliseconds)
CREATE TABLE IF NOT EXISTS nsdf.catalog(

   catalog	       LowCardinality(String),
   bucket	       String,
   name            String,
   size            BIGINT,
   last_modified   String NULL, 
   etag            String NULL,
   inserted_at     DateTime64(3) DEFAULT now64(),

	# max 6 chars allowed
   ext             LowCardinality(String) MATERIALIZED IF( length(splitByChar('.',name)[-1])<=6 , splitByChar('.',name)[-1] , '') 
) 
ENGINE = MergeTree() 
ORDER BY (catalog, bucket, name)
PRIMARY KEY(catalog, bucket, name) 
SETTINGS index_granularity = 8192;


DROP VIEW IF EXISTS nsdf.aggregated_catalog;

CREATE MATERIALIZED VIEW nsdf.aggregated_catalog 
ENGINE = SummingMergeTree
PARTITION BY (catalog)
ORDER BY (catalog, bucket, ext)
POPULATE AS
SELECT catalog, bucket, ext, SUM(size) as tot_size, COUNT(size) as num_files
FROM nsdf.catalog
GROUP BY catalog, bucket, ext
ORDER BY catalog, bucket, ext, tot_size DESC, num_files DESC;
