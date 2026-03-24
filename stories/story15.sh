#!/bin/bash

curl -X POST "http://localhost:8000/generate-video" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "I did not catch my boyfriend cheating. I found out I was being slowly replaced.",
        "type": "story",
        "story": "I did not catch him cheating in some dramatic way. No lipstick, no hotel receipts, nothing like that. We were just on the couch late at night. He fell asleep first. His phone was on the table and it kept vibrating, which was honestly just annoying. I picked it up to mute it. That is when I saw the message preview. Can you still come over tomorrow. I miss you. From a contact saved as A. The phone unlocked before I even thought about it. I did not want to scroll but I did. They had been talking almost every day for close to a year. Not inappropriate messages. Just emotional stuff. Long messages, inside jokes, venting, checking in. About life. About stress. About me. I put the phone back and pretended everything was normal. The next day I searched my own name in his messages. Turns out I was the stable one. The real relationship. She was the one who understood him. That night I asked who she was. She is just a friend, he said. I asked how he would feel if I did the same thing with another guy. He said I was being dramatic. I did not fight. I did not yell. I just left a few days later. He still texts sometimes saying he never actually cheated. Maybe not. But I know what it feels like to slowly be replaced."
    }'
