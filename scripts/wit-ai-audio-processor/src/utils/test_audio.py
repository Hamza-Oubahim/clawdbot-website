"""
Test utilities for Wit.ai Audio Processor
"""

import os
import tempfile
import subprocess
from pathlib import Path

def create_test_audio(duration_seconds=5, sample_rate=16000):
    """
    Create a test WAV file with silence
    Requires sox or ffmpeg
    """
    try:
        # Create temp file
        temp_dir = tempfile.gettempdir()
        test_file = Path(temp_dir) / f"test_audio_{int(os.getenv('WIT_API_KEY_DEFAULT', '0')[-4:])}.wav"
        
        # Try sox first, then ffmpeg
        try:
            # Generate silence with sox
            cmd = ['sox', '-n', '-r', str(sample_rate), '-c', '1', 
                   str(test_file), 'trim', '0.0', str(duration_seconds)]
            subprocess.run(cmd, check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall back to ffmpeg
            cmd = ['ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=16000:cl=mono', 
                   '-t', str(duration_seconds), '-acodec', 'pcm_s16le', 
                   '-y', str(test_file)]
            subprocess.run(cmd, check=True, capture_output=True)
        
        return test_file if test_file.exists() else None
        
    except Exception as e:
        print(f"Error creating test audio: {e}")
        return None

def simulate_whatsapp_audio(phone_number="212626474248", audio_path=None):
    """
    Simulate WhatsApp audio file in incoming directory
    """
    incoming_dir = Path("/root/clawd/audio/incoming")
    incoming_dir.mkdir(parents=True, exist_ok=True)
    
    if audio_path and Path(audio_path).exists():
        # Copy existing audio file
        import shutil
        import time
        timestamp = int(time.time())
        dest_file = incoming_dir / f"{phone_number}_{timestamp}.ogg"
        shutil.copy2(audio_path, dest_file)
        return dest_file
    else:
        # Create a test file
        test_wav = create_test_audio(3)
        if test_wav:
            timestamp = int(time.time())
            dest_file = incoming_dir / f"{phone_number}_{timestamp}.ogg"
            # Convert to OGG (simplified)
            cmd = ['ffmpeg', '-i', str(test_wav), '-c:a', 'libopus', 
                   '-y', str(dest_file)]
            subprocess.run(cmd, capture_output=True)
            test_wav.unlink()  # Clean up temp WAV
            return dest_file if dest_file.exists() else None
    
    return None
