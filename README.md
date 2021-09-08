# <img width="300" src="https://user-images.githubusercontent.com/2439255/132557116-8b47acdc-d259-492f-9c36-c18ac41c8826.png">
Minimalist Error collection Service

## Features
- Compatible with any Rollbar client(see https://docs.rollbar.com/docs). Just change the endpoint URL to your errorpush URL.
- Inserts all error logs into a single PostgreSQL table.

## Why use this over Sentry/Rollbar?
- Instant setup
- Free
- No rate limiting
- Flexibility - use whatever you want to query the PostgresQL table for errors

## Running
errorpush requires docker

```bash
docker run -p 5000:5000 -e ACCESS_TOKEN=<your_access_token_of_choice> -e POSTGRES_URI=postgres://username:password@yourhost.com/yourdb hauxir/errorpush:latest
```
That's it, just set up a reverse proxy and point your rollbar client to your server.
