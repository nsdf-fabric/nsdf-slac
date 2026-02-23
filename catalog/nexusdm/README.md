# NEXUS-DM package

The `nexusdm` package is a program that populates a clickhouse DB with the NEXUS-DM CDMS object data found in the `scientistcloud` bucket.
The following environment variables must be provided:

```yaml
PROFILE_NAME=
ENDPOINT_URL=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
BUCKET_NAME=

CLICKHOUSE_HOST=
CLICKHOUSE_PORT=
CLICKHOUSE_USER=
CLICKHOUSE_DB=
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1
```
