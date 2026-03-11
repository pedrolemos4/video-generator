docker build -t video-pipeline .

docker run -p 8000:8000 `
  -v ${PSScriptRoot}/videos:/app/videos `
  -v ${PSScriptRoot}/stories:/app/stories `
  -v ${PSScriptRoot}/output:/app/output `
  video-pipeline