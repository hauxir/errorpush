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
SELECT error_id, Max(( ( BODY ->> 'trace' ) :: jsonb ->> 'exception' ) :: jsonb ->> 'class') AS EXCEPTION, Max(( ( BODY ->> 'message' ) :: jsonb ->> 'body' )) AS message, Count(*), Max(timestamp) AS last_seen FROM   errors GROUP  BY error_id ORDER  BY last_seen DESC;
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

## Metabase
You can use [metabase](https://github.com/metabase/metabase) to visualize the data.

 <img width="1432" alt="Screenshot 2021-09-11 at 00 14 58" src="https://user-images.githubusercontent.com/2439255/132930119-86a6debe-0b56-43a4-b709-c64d4df24194.png">
 
PostgreSQL view for the above image: 
```sql
create view error_report as 
select 
  error_id, 
  max(
    concat(
      coalesce(
        (
          (body ->> 'trace'):: jsonb ->> 'exception'
        ):: jsonb ->> 'class', 
        'Error'
      ), 
      ': ', 
      (
        (body ->> 'trace'):: jsonb ->> 'exception'
      ):: jsonb ->> 'message', 
      (body ->> 'message'):: jsonb ->> 'body'
    )
  ) as error, 
  count(*) as occurences, 
  max(timestamp) as last_seen, 
  max(
    array_to_string(
      array(
        select 
          concat(
            el ->> 'filename', ':', el ->> 'lineno'
          ) 
        from 
          jsonb_array_elements(
            (
              (body ->> 'trace'):: jsonb ->> 'frames'
            ):: jsonb
          ) as el 
        limit 
          4
      ), 
      ', '
    )
  ) as trace, 
  max(environment) as environment, 
  max(custom ->> 'revision') as revision 
from 
  errors 
group by 
  error_id 
order by 
  last_seen desc;
  ```
