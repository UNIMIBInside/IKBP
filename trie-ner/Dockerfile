FROM python:3.10

WORKDIR /home/app

RUN python3 -m pip install --upgrade pip
    
# Install utils
RUN apt-get update && \
    apt-get -y install --no-install-recommends gcc

COPY . .

RUN pip install --no-cache-dir --upgrade -r /home/app/requirements.txt

CMD python main.py --host 0.0.0.0 --port 80 --path-to-saved-tries "$PATH_TO_SAVED_TRIES" --trie-name "$TRIE_NAME"
