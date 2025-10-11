#!/bin/bash

set -euo pipefail

_w() {
  local -r text="${1-}"
  echo -e "$text"
}


mongosh_connect() {
  _w " ┌────────────────────────────────────┐"
  _w " │  Welcome to the mongosh connector  │"
  _w " └────────────────────────────────────┘"
  _w

    docker run -it --rm mongodb/mongodb-community-server:7.0.12-ubi8 mongosh "$MONGODB_URI"
}

mongosh_connect "$@"
