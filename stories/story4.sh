#!/bin/bash

curl -X POST "http://localhost:8000/generate-video" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "I accidentally found out my 84 year old neighbour used to be a Cold War cryptographer and now we have weekly spy lessons.",
    "type": "story",
    "story": "So I have lived next door to this quiet old man for years. Always polite, keeps his lawn perfect, and waves once in a while. Last month I helped him carry groceries inside and I noticed this massive stack of old notebooks covered in numbers and symbols. I joked, you planning a heist or something. He just smiled and said, I used to do this for a living. Turns out he was a cryptographer for the US during the Cold War. Worked on message encoding systems before computers took over. He told me stories about intercepting Soviet radio chatter, writing ciphers by hand, and decoding messages that came through at 3 AM on paper tape. Now every Thursday evening, I bring over coffee and he teaches me basic cipher techniques. We started with Caesar shifts, then moved to Vigenere and book ciphers. The man is 84 and still does long division faster than I can open Google. It is honestly the most interesting thing I have stumbled into in years. Like having a real life spy mentor living next door."
  }'