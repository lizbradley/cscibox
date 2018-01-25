#!/usr/bin/bash

docker build -t cscibox .
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY --device /dev/snd --name cscibox cscibox

# To get the repository image so you don't have to download the repository from github
# docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY --device /dev/snd --name cscibox suyogsoti/cscibox
