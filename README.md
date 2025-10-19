# Console Radio Player

A Python-based internet radio player with a cool console interface!

## Features
-  Play/Pause 
-  Next/Previous station navigation
-  Looks like your Grandpa's Radio Box
-  Easy station management via text file


## Installation

### 1. Install Dependencies

```bash
pip install pyaudio
```

### 2. Install FFmpeg

**Windows:**
- Download from: https://ffmpeg.org/download.html
- Extract and add `bin` folder to PATH
- Or use stuff like `choco`


## Configuration

Change `stations.txt` to add your favorite radio stations:

```
# Station Name | URL (search in the internet or their website)
My Radio | http://stream.example.com/radio
```

## Usage

Run the player:
```bash
python radio_player.py
```

### Controls
- **N** - Next station
- **P** - Previous station
- **Space** - Pause/Resume
- **Q** - Quit



## Adding Stations

Use these for Western Songs (For Nepali check the stations' website):
- https://streamurl.link/
- https://www.internet-radio.com/
- https://directory.shoutcast.com/


## License
MIT License - Feel free to use and modify!

Enjoy your music! 