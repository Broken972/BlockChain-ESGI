FROM python:alpine3.19

RUN apk update && \
    apk add git openssh

RUN pip install --upgrade pip

RUN adduser --disabled-password -u 1000 user && \
    mkdir -p /home/user/.ssh

COPY ./github_keys/id_rsa_github /home/user/.ssh
COPY ./github_keys/id_rsa_github.pub /home/user/.ssh

RUN chown -R 1000:1000 /home/user/.ssh

USER user

WORKDIR /home/user

RUN GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa_github -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git clone git@github.com:Broken972/BlockChain-ESGI.git

WORKDIR /home/user/BlockChain-ESGI

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "blockchain.py"]