FROM python:3.11-slim

# Install FFmpeg and any other OS-level dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Use an environment variable for your Discord Bot Token.
# Replace 'YOUR_BOT_TOKEN_HERE' with a valid default or pass it during runtime.
ENV DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Run the bot
CMD ["python", "bot.py"]
