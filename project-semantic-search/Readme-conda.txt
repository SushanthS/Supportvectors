
conda create -n py311 --file requirements.txt

conda list -e > requirements.txt
# Install spacy
conda install spacy
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_sm
python -m spacy download en

#Install sentence transformers
conda config --append channels conda-forge
conda install -c conda-forge sentence-transformers

# Additional installations
conda install ruamel
conda install ruamel.yaml


conda install pykwalify

conda install decorator

#Git Configuration for commits
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
