#!/usr/bin/env bash

pip install -r requirements/base.txt
pip-sync requirements/dev.txt
sudo apt-get update
sudo apt install libxcb-xinerama0 libxcb-cursor0 libegl1
