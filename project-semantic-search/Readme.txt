
conda create -n py311 --file requirements.txt

conda list -e > requirements.txt
Install spacy
conda install spacy
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_sm
python -m spacy download en