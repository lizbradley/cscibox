#!/usr/bin/bash

docker build -t cscibox .
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY --device /dev/snd --name cscibox cscibox
