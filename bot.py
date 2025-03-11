import discord
from discord.ext import commands
from discord import app_commands
import os

# Function to parse .pls files
def parse_pls(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.lower().startswith("file1="):
                    return line.split("=", 1)[1].strip()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin1') as f:
                for line in f:
                    if line.lower().startswith("file1="):
                        return line.split("=", 1)[1].strip()
        except Exception as e:
            print(f"Error reading {file_path} with fallback encoding: {e}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None

# Auto-detect .pls files and load streams
STREAMS = {}
for file in os.listdir():
    if file.endswith(".pls"):
        stream_name = os.path.splitext(file)[0]  # Get filename without extension
        STREAMS[stream_name] = parse_pls(file)

for name, url in STREAMS.items():
    if url is None:
        print(f"Warning: No URL loaded for {name} stream!")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="list", description="List all available streams")
async def list_streams(interaction: discord.Interaction):
    available_streams = [s for s in STREAMS.keys() if STREAMS[s] is not None]
    if available_streams:
        streams_list = "\n".join(available_streams)
        await interaction.response.send_message(f"Available streams:\n{streams_list}", ephemeral=True)
    else:
        await interaction.response.send_message("No available streams found.", ephemeral=True)

@bot.tree.command(name="play", description="Play a stream in your voice channel")
@app_commands.describe(stream="Choose a stream")
async def play(interaction: discord.Interaction, stream: str):
    stream = stream.lower()
    if stream not in STREAMS or STREAMS[stream] is None:
        valid = ", ".join([s for s in STREAMS.keys() if STREAMS[s] is not None])
        await interaction.response.send_message(
            f"Invalid stream. Use `/list_streams` to see available options.", ephemeral=True
        )
        return

    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You must be in a voice channel to play a stream.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client
    if vc is None:
        vc = await voice_channel.connect()
    elif vc.channel != voice_channel:
        await vc.move_to(voice_channel)

    ffmpeg_options = {'options': '-vn'}  # No video flag
    stream_url = STREAMS[stream]
    source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)

    if vc.is_playing():
        vc.stop()
    vc.play(source)
    await interaction.response.send_message(f"Now playing the **{stream}** stream.")

@bot.tree.command(name="stop", description="Stop playing and disconnect from the voice channel")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc is None:
        await interaction.response.send_message("I'm not connected to a voice channel.", ephemeral=True)
        return
    vc.stop()
    await vc.disconnect()
    await interaction.response.send_message("Disconnected from the voice channel.")

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    # Set a constant rich presence using the 'listening' activity type.
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="PEAKXEL Radio"
    ))
    print(f"Logged in as {bot.user}")

bot.run(os.environ["DISCORD_BOT_TOKEN"])
