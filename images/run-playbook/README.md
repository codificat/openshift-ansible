# Containerized OpenShift certificate checks

This image uses the [playbook2image](https://github.com/aweiteka/playbook2image) image to containerize the `openshift-ansible` playbooks to execute a playbook that will check internal certificates' expiration dates using the `openshift_certificate_expiry` role.

## Build

1. **OpenShift**:

        oc new-build docker.io/aweiteka/playbook2image~https://github.com/openshift/openshift-ansible
        oc get is openshift-ansible

1. **Docker**:

        cd openshift-ansible
        docker build -t certcheck -f images/certificate-check/Dockerfile .

## Usage

You must provide an inventory and ssh keys.

1. **OpenShift**: The sample job definition in the repo provides the inventory via an URL that is passed in via the `INVENTORY_URL` environment variable, and mounts the ssh keys from a secret called `sshkey` that you would create with:

        oc secrets new-sshauth sshkey --ssh-privatekey=$HOME/.ssh/id_rsa

1. **Docker**:

        docker run --rm -u `id -u` \
               -v $HOME/.ssh/id_rsa:/opt/app-root/src/.ssh/id_rsa:Z \
               -e INVENTORY_URL=http://172.17.0.1/hosts \
               certcheck
