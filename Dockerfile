FROM m.docker-registry.ir/python

WORKDIR /app

COPY requirements.txt .
COPY Makefile .

RUN pip install --upgrade pip
RUN make build_env
RUN make install

COPY . .

EXPOSE 8000

CMD ["make", "run_server"]