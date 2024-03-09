FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN git clone https://github.com/janvdp/google-images-download.git
RUN cd google-images-download && python setup.py install

COPY . .

CMD ["python", "main.py"]
