#!/usr/bin/env bash
set -e

FILE_NAME=$1
TAG=$3
GITHUB_DEPLOY_KEY=$4
GITHUB_ORG_AND_REPO=$5

mkdir -p ~/.ssh

cat <<EOF >~/.ssh/config
Hostname github.com
IdentityFile ~/.ssh/id_rsa
EOF

ssh-keyscan -t rsa github.com > ~/.ssh/known_hosts

git config --global user.email "gitops-update@github.com"
git config --global user.name "GitOps Update User"


echo "$GITHUB_DEPLOY_KEY" > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa

python update.py --file $FILE_NAME --tag $TAG --value $REPO