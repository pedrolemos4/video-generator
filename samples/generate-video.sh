#!/bin/bash

curl -X POST "http://localhost:8000/generate-video" \
  -H "Content-Type: application/json" \
  -d '{"title": "The Lighthouse", "type": "story", "story": "The old lighthouse had been dark for thirty years. Every night, fishermen would navigate by memory, cursing the broken beacon that once guided them home."}'
