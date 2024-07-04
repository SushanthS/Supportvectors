Ray docs:
https://docs.ray.io/en/latest/ray-core/tips-for-first-time.html
https://docs.ray.io/en/latest/serve/index.html

Clean chunk service with ray usage:
1) 
ray start --head --dashboard-host=0.0.0.0

2) python clean_chunk_service-ray.py

3) ./clean_chunk_service-ray-test.sh
-- expected response
{"chunks":[[" a"],[" s"],[" d"],[" f"],[" g"],[" h"],[],[" ."],[" ."],[" ."],[],[" q"],[" w"],[" e"],[" r"],[" t"],[" y"],[],[" ."],[" ."],[" ."],[],[" a"]
,[" s"],[" d"],[" f"],[" g"],[" h"]]}

3.1) python chunker_client_ray.py 
    Updates the database if any file to be chunked

4) ray stop

Postgresql docs:
https://www.baeldung.com/ops/postgresql-docker-setup
https://www.bytebase.com/blog/top-psql-commands-with-examples/
psql -U semanticsearch -p 5432 -h 127.0.0.1 -d semanticsearch
\l
\c semanticsearch
\dt 
Nginx setup:
in setup directory
mtls on mac - https://victoronsoftware.com/posts/mtls-with-apple-keychain/

Netstat notes
-------------
netstat -plnt
tcp        0      0 0.0.0.0:4430.0.0.0:*LISTEN      1350982/nginx: mast
tcp        0      0 0.0.0.0:800.0.0.0:*LISTEN      1350982/nginx: mast

Nginx self signed cert notes
----------------------------
https://medium.com/@dahmearjohnson/create-a-http-s-website-with-nginx-on-ubuntu-22-04-lts-af0d38265230
curl -k https://20.57.164.68 --cert client.crt --key client.key
https://victoronsoftware.com/posts/mtls-with-apple-keychain/ - apple google chrome
https://victoronsoftware.com/posts/mtls-with-windows/ - windows 
