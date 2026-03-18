#!/bin/bash

curl -X POST "http://localhost:8000/generate-video" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "I accidentally joined a mountain hiking group and almost got adopted by them",
    "type": "story",
    "story": "So last month I went to a state park to clear my head. I just wanted a simple two mile trail, nothing extreme. I am standing at the trailhead tying my shoes when a group of about ten people in matching neon windbreakers come marching past me. They all wave and say, you must be the new guy. Now I could have said nope, just here on my own. But instead my socially awkward brain panicked and I just nodded. Next thing I know I am being handed a granola bar and introduced to the Wednesday Warriors hiking club. Here is the thing, I do not even like hiking. My water bottle was half full and my idea of exercise is carrying groceries in one trip. But these people are power walking uphill, telling jokes, sharing trail mix, like they have been training for this since birth. I am sweating by the first incline. About halfway up one of them asks, so what made you want to join us. And my dumb mouth goes, oh I have always wanted to push myself. Now they are clapping me on the back like I am Rocky Balboa. One woman literally yells, we have got a fighter. Meanwhile I am quietly trying not to faint. Three hours later I am at the top of a mountain with ten strangers eating orange slices like I am at soccer practice. They are talking about next weeks twelve mile challenge and asking if I will be there. I just smile and say we will see. I never saw them again. But somewhere out there the Wednesday Warriors think I am training for a marathon, when in reality I went home, collapsed on the couch, and ordered pizza."
  }'
