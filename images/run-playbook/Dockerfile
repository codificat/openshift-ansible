FROM docker.io/aweiteka/playbook2image:latest

# The playbook to be run is specified via the PLAYBOOK_FILE env var
# Setting a default of openshift_facts.yml here
ENV PLAYBOOK_FILE=plabyooks/byo/openshift_facts.yml \
    ANSIBLE_HOST_KEY_CHECKING=False \
    OPTS="-v"

ADD . ${APP_HOME}

CMD [ "/usr/libexec/s2i/run" ]
