#!/bin/bash

# start mongo here in the background
mongod &

python /home/user/app/src/cscibox.py

# Stop mongo here
pkill mongod
