# Running Locally with Docker Compose (dev)

All the components can be deployed locally using using Docker Compose. You will need to provide the environment variables for the Postgres database via a `.env` file, and example its provided at `.env.example`.

First, run the following commands to build the images:

```bash
make build
make buildseed
```

Then, run the following command:

```bash
make up
```

This will spawn up the UI, Postgres Server, and seed the Postgres DB with synthetic data.

## Seed with Nexus-DM data (Optional)

You will need to have **Golang>=1.25.3**. You can download Go [here](https://go.dev/dl/)

To seed with data from s3, build the nexus seed binary.

```
make nexusseed
```

Then, run the seed program.

```
make nexus
```

## Cleanup

To cleanup the project, you can run:

```bash
make down
```
