FROM python:3.7

WORKDIR /app/

RUN apt-get update -y

RUN apt-get install default-jdk -y

RUN apt-get install perl -y

COPY ./package/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir git+https://github.com/JMendes1995/py_heideltime.git

RUN chmod 111 -R /usr/local/lib/python3.7/site-packages/py_heideltime/Heideltime/TreeTaggerLinux/bin/*

# Run fix to install neuralcoref
# The fix - https://github.com/huggingface/neuralcoref/issues/222
RUN git clone https://github.com/huggingface/neuralcoref.git

RUN pip install --no-cache-dir -r ./neuralcoref/requirements.txt

RUN pip install --no-cache-dir -e ./neuralcoref
# End of fix

RUN pip install --no-cache-dir -r requirements.txt

# RUN pip install --no-cache-dir --upgrade spark-nlp

RUN pip install --no-cache-dir nlpnet==1.2.4

RUN python -m nltk.downloader averaged_perceptron_tagger

COPY . .

EXPOSE 65432

CMD ["python", "-u", "server.py"]
