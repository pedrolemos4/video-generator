#!/bin/bash

VIDEO="./videos/video1.mp4"

curl -X POST "http://localhost:8000/upload-video" \
  -F "file=@${VIDEO}"
