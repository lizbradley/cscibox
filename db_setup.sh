#!/usr/bin/sh

mongod &

cd src
python dbrestore.py

pkill mongod
