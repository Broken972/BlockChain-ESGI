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

#Ici le -u permet de désactiver un buffer étrange de python3 quand dockerizé sans cette option les appels print ne remontent pas dans stdout
CMD ["python3","-u","blockchain.py"]