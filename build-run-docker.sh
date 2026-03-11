#!/bin/bash

docker build -t video-pipeline .

docker run -p 8000:8000 \
  -v ./videos:/app/videos \
  -v ./stories:/app/stories \
  -v ./output:/app/output \
  video-pipeline
