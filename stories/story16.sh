#!/bin/bash

curl -X POST "http://localhost:8000/generate-video" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "My coworker kept criticizing my work in front of the boss so one day I just let him do the whole thing himself",
        "type": "story",
        "story": "I work at a small company where our team prepares monthly reports. The job is not very complicated but it requires attention to detail and time. We have one coworker who always likes to act like the expert. At almost every meeting he would find something to criticize in my reports. He did not like the wording, the table did not look right, or something else. Because of that the boss started thinking that he actually understood the work better than everyone else. One time before the next report he again started saying that he could do it much more efficiently. I simply said, okay then you can prepare this report. The boss agreed because he thought it was a good idea. During that week my coworker acted very confident. He even said a few times that he would now show everyone how the job should really be done. When the day of the presentation came the problems started. The report had missing data, several tables did not match, and one of the graphs was completely incorrect. The boss started asking questions that my coworker could not properly answer. In the end the meeting finished with the report needing to be redone. After that he criticizes other people work in meetings much less often. And now the boss pays more attention to who actually did the work instead of just listening to the loudest person in the room. Honestly I did not even do anything special. I just gave him the chance to show his level."
    }'
