FROM python:3.10

WORKDIR /home/app

RUN python3 -m pip install --upgrade pip
    
# Install utils
RUN apt-get update && \
    apt-get -y install --no-install-recommends gcc

COPY . .

RUN pip install --no-cache-dir --upgrade -r /home/app/requirements.txt

CMD python main.py --host 0.0.0.0 --port 80 --path-to-type-relation-csv "$PATH_TO_TYPE_RELATION_CSV" --path-to-annset-priority "$PATH_TO_ANNSET_PRIORITY" --path-to-types "$PATH_TO_TYPES"
