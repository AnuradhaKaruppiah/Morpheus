#/usr/bin/env bash

usage() {
  echo "Usage: $(basename $0) [MORPHEUS_USER] [MORPHEUS_USER_PW]"
  exit
}

create_user() {
  if [ "$MORPHEUS_USER" == "root" ]; then
    echo "User specified as 'root', skipping creation..."
    exit
  fi

  useradd -ms /workspace $MORPHEUS_USER
}

if [[ $# -ne 1 ]]; then
  usage
fi

MORPHEUS_USER="$1"

create_user
