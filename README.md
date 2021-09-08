# <img width="300" src="https://user-images.githubusercontent.com/2439255/132557116-8b47acdc-d259-492f-9c36-c18ac41c8826.png">
Minimalist Error collection Service

## Features
- Compatible with any Rollbar client(see https://docs.rollbar.com/docs). Just change the endpoint URL to your errorpush URL.
- Inserts all error logs into a single PostgreSQL table.

## Why use this over Sentry/Rollbar?
- Instant setup
- Free
- No rate limiting
- When you don't need all the bells and whistles: just want to log all errors into a database.
- Flexibility - use whatever you want to query the PostgresQL table for errors

## Running
errorpush requires docker

```bash
docker run -p 5000:5000 -e ACCESS_TOKEN=<your_access_token_of_choice> -e POSTGRES_URI=postgres://username:password@yourhost.com/yourdb hauxir/errorpush:latest
```
That's it, just set up a reverse proxy and point your rollbar client to your server.

## Example Query
```sql
SELECT error_id, MAX(exception ->> 'class') AS exception, MAX(message ->> 'body') AS message, COUNT(*), MAX(timestamp) AS last_seen FROM errors GROUP BY error_id ORDER BY MAX(timestamp) DESC;
```
```
             error_id             | exception |   message    | count |         last_seen          
----------------------------------+-----------+--------------+-------+----------------------------
 8cca0a18f56269b5a5243f7cc2906f79 | NameError |              |     4 | 2021-09-08 18:34:05.751548
 b6012c1be2bef37f570077f2ce2e908b |           |              |     2 | 2021-09-08 18:15:09.944348
 5acf76ad5f327d811ca9282b5d5a933a |           | Hello world! |     3 | 2021-09-08 18:15:09.944308
 794ef3b916db810d9162ad54aff32a14 |           | HEY          |     1 | 2021-09-08 18:12:19.705926
(4 rows)
```
