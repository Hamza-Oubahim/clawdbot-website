#!/usr/bin/env python3
"""
Test script for audio processing
"""

import os
import subprocess
import json
import time

# Get OpenAI API key from environment or config
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    # Try to read from config
    try:
        with open("/root/.clawdbot/clawdbot.json", "r") as f:
            config = json.load(f)
            openai_key = config.get("env", {}).get("vars", {}).get("OPENAI_API_KEY")
    except:
        pass

print("=" * 60)
print("AUDIO PROCESSING TEST")
print("=" * 60)

# Test audio file
audio_file = "/root/clawd/audio/incoming/212635278125_1769654518.ogg"
print(f"Audio file: {audio_file}")
print(f"File exists: {os.path.exists(audio_file)}")
print(f"File size: {os.path.getsize(audio_file)} bytes")

# Check FFmpeg
print("\n" + "-" * 40)
print("FFmpeg check:")
try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    print("✅ FFmpeg installed")
    print(f"Version: {result.stdout.split('\\n')[0]}")
except:
    print("❌ FFmpeg not installed")

# Check OpenAI API key
print("\n" + "-" * 40)
print("OpenAI API key check:")
if openai_key:
    print(f"✅ API key found: {openai_key[:20]}...")
    
    # Test Whisper API
    print("\n" + "-" * 40)
    print("Testing Whisper API...")
    
    try:
        import openai
        openai.api_key = openai_key
        
        # First convert OGG to WAV
        wav_file = audio_file.replace('.ogg', '.wav')
        cmd = [
            'ffmpeg', '-i', audio_file,
            '-ar', '16000',
            '-ac', '1',
            '-acodec', 'pcm_s16le',
            '-y',
            wav_file
        ]
        
        print(f"Converting {audio_file} to WAV...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(wav_file):
            print(f"✅ Converted to WAV: {wav_file}")
            print(f"WAV size: {os.path.getsize(wav_file)} bytes")
            
            # Try to transcribe
            print("\nTranscribing with Whisper API...")
            try:
                with open(wav_file, "rb") as audio:
                    transcript = openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio,
                        language="ar",  # Arabic for Darija
                        response_format="text"
                    )
                
                print("=" * 60)
                print("✅ TRANSCRIPTION SUCCESSFUL!")
                print("=" * 60)
                print(f"Transcript: {transcript}")
                print("=" * 60)
                
                # Save transcript
                transcript_file = audio_file.replace('.ogg', '.txt')
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                print(f"Transcript saved to: {transcript_file}")
                
                # Clean up WAV file
                os.remove(wav_file)
                
            except Exception as e:
                print(f"❌ Whisper API error: {e}")
                print("This could be due to:")
                print("1. Invalid API key")
                print("2. Audio format issues")
                print("3. API quota exceeded")
                print("4. Network issues")
        else:
            print(f"❌ Conversion failed: {result.stderr}")
            
    except ImportError:
        print("❌ OpenAI library not installed")
        print("Install with: pip install openai")
    except Exception as e:
        print(f"❌ Error: {e}")
        
else:
    print("❌ No OpenAI API key found")
    print("Set OPENAI_API_KEY environment variable or add to config")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)