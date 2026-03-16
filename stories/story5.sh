#!/bin/bash

curl -X POST "http://localhost:8000/generate-video" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "How a Janitor Changed My Life Without a Word",
    "type": "story",
    "story": "I was homeless for six months in 2011. I slept in my car. I used to park behind a small church because it was dark and quiet. I thought nobody knew I was there. Every morning I would wake up, drive to a gas station to wash my face, and go to work. Yes, I had a job, just could not afford rent. One night it was freezing. Ten degrees. My car would not start to run the heater. I was shivering so hard my teeth hurt. I saw the back door of the church open. A janitor came out to dump the trash. He saw my car. He saw me huddled in the front seat. He did not call the cops. He did not come over and tap on the window. He just walked back to the door, unlocked it, and propped it open with a small rock. Then he turned on the hallway light and left. I waited ten minutes. Then I ran inside. It was warm. There was a couch in the lobby. There was a bathroom with hot water. I slept there every night for the rest of the winter. Every night, the rock was there. I never met the janitor. I never thanked him. I am back on my feet now. I have a house. I have a bed. But every year on the first snow, I donate a check to that church. I write for the heating bill in the memo line. Sometimes the loudest way to love your neighbor is to say nothing at all."
  }'