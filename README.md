
# PEAKXEL Radio

A Discord Music Bot solution for playing HLS streams.

I used AzuraCast to create my own HLS streams.

Place your .pls files in the root path of this project, you will need to change the python code to match the name of your .pls files.






## Deployment

First you need to build your docker image and then you can deploy.

```bash
  docker build -t peakxel_radio .
  docker run -e YOUR_BOT_KEY peakxel_radio
```

