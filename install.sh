#!/usr/bin/bash

docker build -t cscibox .
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY --device /dev/snd --name cscibox cscibox

# follow directions for x-server here: https://fredrikaverpil.github.io/2016/07/31/docker-for-mac-and-gui-applications/
# ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}') xhost + $ip
# docker run -d --name cscibox -e DISPLAY=$ip:0 -v /tmp/.X11-unix:/tmp/.X11-unix cscibox


# for windows: https://manomarks.github.io/2015/12/03/docker-gui-windows.html
