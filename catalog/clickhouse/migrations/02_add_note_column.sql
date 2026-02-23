ALTER TABLE nsdf.catalog
ADD COLUMN note String DEFAULT '' AFTER inserted_at;
