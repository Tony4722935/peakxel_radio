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

# Keep track of default volume per guild (0.0 to 2.0). Defaults to 0.5 (50%).
DEFAULT_VOLUME = 0.5
guild_volumes = {}

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
            f"Invalid stream. Use `/list` to see available options.", ephemeral=True
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

    stream_url = STREAMS[stream]

    # FFmpeg reconnect and buffering options to reduce lag/interruptions
    ffmpeg_before_options = (
        "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    )
    ffmpeg_options = "-vn -bufsize 1024k"

    # Create a PCM source and wrap it in a volume transformer
    pcm_source = discord.FFmpegPCMAudio(
        stream_url,
        before_options=ffmpeg_before_options,
        options=ffmpeg_options
    )
    volume = guild_volumes.get(interaction.guild.id, DEFAULT_VOLUME)
    player = discord.PCMVolumeTransformer(pcm_source, volume=volume)

    if vc.is_playing() or vc.is_paused():
        vc.stop()
    vc.play(player)

    await interaction.response.send_message(f"Now playing the **{stream}** stream at {int(volume * 100)}% volume.")

@bot.tree.command(name="stop", description="Stop playing and disconnect from the voice channel")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc is None:
        await interaction.response.send_message("I'm not connected to a voice channel.", ephemeral=True)
        return
    vc.stop()
    await vc.disconnect()
    await interaction.response.send_message("Disconnected from the voice channel.")

@bot.tree.command(name="volume", description="Adjust the playback volume (0.0 to 2.0)")
@app_commands.describe(level="Volume multiplier: 0.0 (mute) to 2.0 (200%)")
async def volume(interaction: discord.Interaction, level: float):
    vc = interaction.guild.voice_client
    if vc is None or not vc.is_playing():
        await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
        return

    if level < 0.0 or level > 2.0:
        await interaction.response.send_message("Please provide a volume between 0.0 and 2.0.", ephemeral=True)
        return

    # Ensure the source is wrapped in a PCMVolumeTransformer
    source = vc.source
    if not isinstance(source, discord.PCMVolumeTransformer):
        # If somehow it's not wrapped (unlikely), wrap it now
        wrapped = discord.PCMVolumeTransformer(source, volume=level)
        vc.source = wrapped
    else:
        source.volume = level

    guild_volumes[interaction.guild.id] = level
    await interaction.response.send_message(f"Volume set to {int(level * 100)}%.")

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
