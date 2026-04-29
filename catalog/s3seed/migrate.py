import os
import gzip
import io
import boto3
import psycopg
import logging

logging.basicConfig(
    filename="migration.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("ENDPOINT_URL"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "catalog"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "mypassword"),
    )


def create_staging_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS staging_catalog (
                catalog TEXT,
                bucket TEXT,
                name TEXT,
                size BIGINT,
                last_modified TEXT,
                etag TEXT
            );
            """
        )
    conn.commit()


def process_file(s3_client, conn, bucket, key: str):
    logging.info(f"Processing: {key}")

    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)

        body = obj["Body"]
        if key.endswith("gz"):
            body = gzip.GzipFile(fileobj=obj["Body"])

        text_stream = io.TextIOWrapper(body, encoding="utf-8", errors="ignore")

        with conn.cursor() as cur:
            # COPY into staging
            with cur.copy(
                """
                COPY staging_catalog (catalog, bucket, name, size, last_modified, etag)
                FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                """
            ) as copy:
                for line in text_stream:
                    line = line.replace("\x00", "")
                    if not line.strip(): 
                        continue

                    if line.count(",") == 5:
                        copy.write(line)

            # Merge into main table
            cur.execute(
                """
                INSERT INTO catalog (catalog, bucket, name, size, last_modified, etag)
                SELECT DISTINCT ON (catalog, bucket, name) catalog, bucket, name, size, last_modified, etag
                FROM staging_catalog
                ON CONFLICT (catalog, bucket, name)
                DO UPDATE SET
                    size = EXCLUDED.size,
                    last_modified = EXCLUDED.last_modified,
                    etag = EXCLUDED.etag
                WHERE catalog.size IS DISTINCT FROM EXCLUDED.size
                   OR catalog.last_modified IS DISTINCT FROM EXCLUDED.last_modified
                   OR catalog.etag IS DISTINCT FROM EXCLUDED.etag;
                """
            )

            # Clear staging for next file
            cur.execute("TRUNCATE staging_catalog;")

        conn.commit()
        logging.info(f"Finished: {key}")

    except Exception as e:
        conn.rollback()
        logging.error(f"Error processing {key}: {e}")


def insert_records(s3_client, conn, bucket="nsdf-catalog"):
    paginator = s3_client.get_paginator("list_objects_v2")

    objects = []
    for page in paginator.paginate(Bucket=bucket):
        objects.extend(page.get("Contents", []))

    for obj in objects:
        process_file(s3_client, conn, bucket, obj["Key"])


def main():
    s3_client = get_s3_client()
    conn = get_db_connection()

    create_staging_table(conn)
    insert_records(s3_client, conn)

    conn.close()


if __name__ == "__main__":
    main()
