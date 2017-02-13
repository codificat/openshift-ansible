FROM docker.io/aweiteka/playbook2image:latest

ENV PLAYBOOK_FILE=playbooks/certificate_expiry/default.yaml \
    ANSIBLE_HOST_KEY_CHECKING=False \
    OPTS="-v"

ADD . /opt/app-root/src/

CMD [ "/usr/libexec/s2i/run" ]
