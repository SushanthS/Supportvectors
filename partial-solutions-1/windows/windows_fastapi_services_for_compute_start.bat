start /B %PYTHON_HOME%/python.exe %BOOTCAMP_ROOT_DIR%/svlearn/service/rest/fastapi/clean_chunk_fastapi_service.py > NUL
start /B %PYTHON_HOME%/python.exe %BOOTCAMP_ROOT_DIR%/svlearn/service/rest/fastapi/sentence_embedding_fastapi_service.py > NUL
start /B %PYTHON_HOME%/python.exe %BOOTCAMP_ROOT_DIR%/svlearn/service/rest/fastapi/faiss_index_builder_fastapi_service.py > NUL
set es_home_wsl=%ES_HOME_WSL%
wsl nohup %es_home_wsl%/bin/elasticsearch &
