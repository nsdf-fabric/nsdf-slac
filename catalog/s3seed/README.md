# S3 Seed

The `s3seed` package provides an interface to migrate `nsdf-catalog` data from clickhouse to postgresql.

## PostgreSQL

Start a postgreSQL database with compose.

> > NOTE
> > Provide a sufficient storage on the host for the data typically 2TB

```bash
make up
```

## Migration

Now we can start the migration script.

> > IMPORTANT
> > Provide crendentials via on the `.env` checkout .env.example

```bash
make migrate
```

## Cleanup

Cleanup with the following:

```bash
make down
```
