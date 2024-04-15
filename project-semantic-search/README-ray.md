Ray docs:
https://docs.ray.io/en/latest/ray-core/tips-for-first-time.html
https://docs.ray.io/en/latest/serve/index.html

Clean chunk service with ray usage:
1) ray start --head
2) python clean_chunk_service-ray.py
3) ./clean_chunk_service-ray-test.sh
-- expected response
{"chunks":[[" a"],[" s"],[" d"],[" f"],[" g"],[" h"],[],[" ."],[" ."],[" ."],[],[" q"],[" w"],[" e"],[" r"],[" t"],[" y"],[],[" ."],[" ."],[" ."],[],[" a"]
,[" s"],[" d"],[" f"],[" g"],[" h"]]}
4) ray stop
