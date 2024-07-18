FROM python:alpine3.19

RUN apk update && \
    apk add git openssh gcc python3-dev libc-dev musl-dev linux-headers

RUN pip install uv

RUN adduser --disabled-password -u 1000 user && \
    mkdir -p /home/user/.ssh

# COPY ./github_keys/id_rsa_github /home/user/.ssh
# COPY ./github_keys/id_rsa_github.pub /home/user/.ssh

RUN chown -R 1000:1000 /home/user/.ssh

#RUN chmod 400 /home/user/.ssh/id_rsa_github

COPY ./code/requirements.txt .

RUN uv pip install --system -r requirements.txt

USER user

WORKDIR /home/user/BlockChain-ESGI/

CMD ["uvicorn","blockchain:app","--port","5000","--host","0.0.0.0","--reload","--ssl-keyfile","./keys/node_tls.key","--ssl-certfile","./keys/node_tls.crt"]