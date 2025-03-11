
# PEAKXEL Radio

A Discord Music Bot solution for playing HLS streams.

I used AzuraCast to create my own HLS streams.

Place your .pls files in the root path of this project






## Deployment

First you need to build your docker image and then you can deploy.

```bash
  docker build -t peakxel_radio .
  docker run -d --restart unless-stopped -e DISCORD_BOT_TOKEN="your_token_here" peakxel_radio
```
## Extra instructions

You likely also want assistance on creating your discord bot.

Visit https://discord.com/developers/applications

-> New Application

Within your Application

-> BOT 

-> Enable everything in Privileged Gateway Intents and grab your Token too

-> OAuth2

Select the following:

Scope: bot, applications.commands.

Bot Permission: Administrator.
