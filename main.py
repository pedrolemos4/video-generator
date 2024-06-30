import json
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import praw

import generate_audio, generate_video


class UrlItem(BaseModel):
    url: str


with open("secrets.json") as f:
    secrets = json.load(f)

reddit = praw.Reddit(
    client_id=secrets["client_id"],
    client_secret=secrets["client_secret"],
    password=secrets["password"],
    user_agent=secrets["user_agent"],
    username=secrets["username"],
)

app = FastAPI()


@app.post("/gen-from-url")
async def video_gen_from_url(url: UrlItem):
    print("Video to generate: " + url.url)

    submission_id = url.url.split("/")[6]
    submission = reddit.submission(id=submission_id)

    thread_text = submission.selftext

    output_filenames = generate_audio.generate_audio(thread_text)

    if len(output_filenames) > 1:
        allFiles = ""
        for filename in output_filenames:
            generate_video.generate_video(filename)
            allFiles += filename + ";"

        return f"Action succedded. Files are named: {(output_filenames.split('\\')[-1]).split('.')[0]}.mp4"
    else:
        generate_video.generate_video(output_filenames[0])
        return f"Action succedded. File is named: {(output_filenames[0].split('\\')[-1]).split('.')[0]}.mp4"


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9016,
        # ssl_certfile=path_to_ssl_cert,
        # ssl_keyfile=path_to_ssl_key,
        reload=True,
    )
