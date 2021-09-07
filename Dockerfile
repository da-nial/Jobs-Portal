FROM m.docker-registry.ir/python

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
COPY Makefile .

RUN pip install --upgrade pip
RUN make install

COPY . .

EXPOSE 8000

CMD ["make", "run_server"]
