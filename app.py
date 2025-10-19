import subprocess
import pyaudio
import threading
import queue
import sys
import shutil
import time
import os
from datetime import datetime

class RadioPlayer:
    def __init__(self, stations_file='stations.txt'):
        self.stations = self.load_stations(stations_file)
        self.current_station_idx = 0
        self.ffmpeg_process = None
        self.audio_stream = None
        self.p = None
        self.audio_queue = queue.Queue(maxsize=50)
        self.is_playing = False
        self.is_paused = False
        self.reader_thread = None
        self.ffmpeg_path = shutil.which('ffmpeg')
        
        if not self.ffmpeg_path:
            print("ERROR: ffmpeg needs to be installed and path!")
            sys.exit(1)
    
    def load_stations(self, filename):
        """Load radio stations from stations.txt"""
        stations = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'): # comments
                        parts = line.split('|')
                        if len(parts) == 2:
                            name, url = parts
                            stations.append({'name': name.strip(), 'url': url.strip()})
        except FileNotFoundError:
            print(f"ERROR: {filename} not found!")
            print("Creating an example file...")
            self.create_example_file(filename)
            sys.exit(1)
        
        if not stations:
            print("No stations found in file.")
            sys.exit(1)
        
        return stations
    
    def create_example_file(self, filename):
        """Create example stations file"""
        example = """# Radio Stations Sample File
# Format: Station Name | Stream URL
# One station per line and # for comment

Ujyalo Network | http://stream.zeno.fm/wtuvp08xq1duv
Nepal Bani FM | https://live.itech.host:8681/stream
"""
        with open(filename, 'w') as f:
            f.write(example)
        print(f"Created {filename} with example stations")
    
    def read_ffmpeg_output(self):
        """Read from ffmpeg in a separate thread"""
        try:
            while self.is_playing:
                data = self.ffmpeg_process.stdout.read(4096)
                if not data:
                    break
                if not self.is_paused:
                    self.audio_queue.put(data)
        except Exception as e:
            pass
        finally:
            self.audio_queue.put(None)
    
    def print_banner(self):
        """Print banner"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                    🎵 RADIO PLAYER  🎵                    ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
    
    def print_visualizer(self):
        """Print simple audio visualizer"""
        bars = "█▓▒░" # lol
        import random
        viz = ''.join(random.choice(bars) for _ in range(40))
        return f"  ♪♫ {viz} ♫♪"
    
    def print_status(self):
        """Print current status"""
        station = self.stations[self.current_station_idx]
        status = "⏸ PAUSED " if self.is_paused else "▶ PLAYING"
        
        print(f"\n  {status}")
        print(f"  Station: {station['name']}")
        print(f"  [{self.current_station_idx + 1}/{len(self.stations)}]")
        print(f"  Tme: {datetime.now().strftime('%H:%M:%S')}")
        
        if not self.is_paused:
            print(f"\n{self.print_visualizer()}")
        print("\n" + "─" * 60)
        print("  Controls: [N]ext | [P]revious | [Space]Pause | [Q]uit")
        print("─" * 60)
    
    def start_station(self):
        """Start playing current station"""
        station = self.stations[self.current_station_idx]
        
    
        self.stop_stream()
        
        # queue clearing
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break
        
        # Start ffmpeg
        self.ffmpeg_process = subprocess.Popen([
            self.ffmpeg_path,
            '-i', station['url'],
            '-f', 's16le',
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            '-loglevel', 'error',
            '-'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        self.is_playing = True
        self.is_paused = False
        
        #  reader thread
        self.reader_thread = threading.Thread(target=self.read_ffmpeg_output, daemon=True)
        self.reader_thread.start()
        
        #  audio
        if not self.p:
            self.p = pyaudio.PyAudio()
        
        if not self.audio_stream:
            self.audio_stream = self.p.open(
                format=pyaudio.paInt16,
                channels=2,
                rate=44100,
                output=True,
                frames_per_buffer=4096
            )
    
    def stop_stream(self):
        """Stop current stream"""
        self.is_playing = False
        
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=2)
            except:
                self.ffmpeg_process.kill()
            self.ffmpeg_process = None
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.is_paused = not self.is_paused
    
    def next_station(self):
        """Switch to next station"""
        self.current_station_idx = (self.current_station_idx + 1) % len(self.stations)
        self.start_station()
    
    def previous_station(self):
        """Switch to previous station"""
        self.current_station_idx = (self.current_station_idx - 1) % len(self.stations)
        self.start_station()
    
    def play_audio(self):
        """Main audio playback loop"""
        try:
            while self.is_playing:
                try:
                    audio_data = self.audio_queue.get(timeout=1)
                    
                    if audio_data is None:
                        break
                    
                    if not self.is_paused and self.audio_stream:
                        self.audio_stream.write(audio_data)
                        
                except queue.Empty:
                    continue
                    
        except Exception as e:
            print(f"Playback error: {e}")
    
    def run(self):
        self.print_banner()
        print("  Loading stations...")
        time.sleep(1)
      
        self.start_station()
        
    
        playback_thread = threading.Thread(target=self.play_audio, daemon=True)
        playback_thread.start()
        
        # buffer time
        time.sleep(2)
        
        # loop
        last_update = time.time()
        
        try:
            if os.name == 'nt': #wind
                import msvcrt
            else: # others, i don't really care for them 
                import termios
                import tty
                import select
            
            while self.is_playing:
                if time.time() - last_update > 1:
                    self.print_banner()
                    self.print_status()
                    last_update = time.time()
            
                if os.name == 'nt':  # Windows
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').lower()
                        self.handle_key(key)
                else: # unix
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1).lower()
                        self.handle_key(key)
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
    
    def handle_key(self, key):
        """Handle keyboard input"""
        if key == 'q':
            self.is_playing = False
        elif key == 'n':
            self.next_station()
        elif key == 'p':
            self.previous_station()
        elif key == ' ':
            self.toggle_pause()
    
    def cleanup(self):
        """Clean up resources"""
        print("\n\nStopping...")
        self.stop_stream()
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        
        if self.p:
            self.p.terminate()
        print("Goodbye! 👋")


if __name__ == "__main__":
    player = RadioPlayer('stations.txt')
    player.run()