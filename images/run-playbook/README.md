# Containerized openshift-ansible to run generic playbooks

This image uses the [playbook2image](https://github.com/aweiteka/playbook2image) image to containerize `openshift-ansible`. The resulting image can run any of the provided playbooks, specified via the PLAYBOOK_FILE environment variable.

## Build

1. **Docker**:

        cd openshift-ansible
        docker build -t certcheck -f images/certificate-check/Dockerfile .

1. **OpenShift**:

        oc new-build docker.io/aweiteka/playbook2image~https://github.com/openshift/openshift-ansible
        oc get is openshift-ansible

## Usage

You must provide:

- an inventory file
- ssh keys
- the playbook to run via the PLAYBOOK_FILE environment variable

Here is an example on how to use the containerized `openshift-ansible` to execute a playbook that will check internal certificates' expiration dates using the `openshift_certificate_expiry` role.

1. **Docker**:

        docker run --rm -u `id -u` \
               -v $HOME/.ssh/id_rsa:/opt/app-root/src/.ssh/id_rsa:Z \
               -e INVENTORY_URL=http://172.17.0.1/hosts \
               -e PLAYBOOK_FILE=playbooks/certificate_expiry/default.yaml \
               certcheck

1. **OpenShift**: The sample job definition in the repo provides the inventory via an URL that is passed in via the `INVENTORY_URL` environment variable, and mounts the ssh keys from a secret called `sshkey` that you would create with:

        oc secrets new-sshauth sshkey --ssh-privatekey=$HOME/.ssh/id_rsa
