1. sudo dnf update
2. download and install latest anaconda
3. get latest java from open jdk
4. spark setup
5. relational store (mariadb) setup
6. get the latest mysql jdbc driver
7. download the solution from course portal
8. import schema sql from solution to create schema in mariadb
9. elastic search setup
10. open VS code, open any python file from solution, then click on the python version specified in lower right of vs code.  This opens preferences to specify the python virtual environment - choose the latest anaconda python installed (you can choose to create a conda virtual environment if you want here).
11. pip install -r requirements.txt (requirements.txt in the root directory of solution)
12. pip install -e . (in root directory of solution after opening a terminal within vs code)
13. update the bootcamp-config.yaml to point to your directories and user/password etc.
14. python -m spacy download <model_name> (<model_name> to be replaced by "en-sm..." )
15. start your services (under svlearn/service/rest/fastapi or svlearn/service/rest/rayserve )
16. now you are ready to run your bootcamp jobs (under svlearn/compute)