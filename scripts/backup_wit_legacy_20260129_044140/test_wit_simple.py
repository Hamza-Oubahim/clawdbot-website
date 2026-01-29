#!/usr/bin/env python3
"""
Simple test of Wit.ai transcription
"""

import os
import json
import requests
import tempfile
import subprocess

def test_wit_transcription():
    # Get API key
    api_key = os.getenv('WIT_API_KEY_DEFAULT')
    if not api_key:
        print("❌ No WIT_API_KEY_DEFAULT found in environment")
        return
    
    print(f"✅ Using Wit.ai API key: {api_key[:10]}...")
    
    # Test audio file
    audio_path = '/root/.clawdbot/media/inbound/8ff63e0d-e17a-4a47-899a-ec41e1a4dcaa.ogg'
    
    # Convert to WAV
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        wav_path = f.name
    
    print(f"Converting {audio_path} to WAV...")
    result = subprocess.run(
        ['ffmpeg', '-i', audio_path, '-ar', '16000', '-ac', '1', 
         '-sample_fmt', 's16', wav_path, '-y', '-hide_banner', '-loglevel', 'error'],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"❌ FFmpeg conversion failed: {result.stderr}")
        return
    
    print(f"✅ Converted to WAV: {wav_path}")
    
    # Get file size
    file_size = os.path.getsize(wav_path)
    print(f"File size: {file_size} bytes")
    
    # Send to Wit.ai
    print("Sending to Wit.ai...")
    with open(wav_path, 'rb') as f:
        audio_data = f.read()
    
    try:
        response = requests.post(
            'https://api.wit.ai/speech',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'audio/wav'
            },
            data=audio_data,
            timeout=30
        )
        
        print(f"✅ Response status: {response.status_code}")
        print(f"Response length: {len(response.text)} characters")
        
        # Save raw response for debugging
        with open('/tmp/wit_raw_response.txt', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Raw response saved to /tmp/wit_raw_response.txt")
        
        # Try to parse as NDJSON
        lines = response.text.strip().split('\n')
        print(f"Number of lines: {len(lines)}")
        
        # Look for JSON objects
        transcripts = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Skip non-JSON lines (might be binary or curl progress)
            if not line.startswith('{'):
                continue
            
            try:
                data = json.loads(line)
                if 'text' in data:
                    transcript_type = data.get('type', 'UNKNOWN')
                    text = data['text']
                    transcripts.append((transcript_type, text))
                    print(f"Line {i}: type={transcript_type}, text={text}")
            except json.JSONDecodeError as e:
                # Try to find where JSON might start
                if '{' in line:
                    json_start = line.find('{')
                    try:
                        data = json.loads(line[json_start:])
                        if 'text' in data:
                            transcript_type = data.get('type', 'UNKNOWN')
                            text = data['text']
                            transcripts.append((transcript_type, text))
                            print(f"Line {i} (fixed): type={transcript_type}, text={text}")
                    except:
                        pass
        
        # Find final transcript
        final_transcript = None
        for ttype, text in transcripts:
            if ttype in ['FINAL_TRANSCRIPTION', 'FINAL_UNDERSTANDING']:
                final_transcript = text
                break
        
        if not final_transcript and transcripts:
            # Use the last transcript if no final found
            final_transcript = transcripts[-1][1]
        
        if final_transcript:
            print(f"\n🎉 FINAL TRANSCRIPT: {final_transcript}")
            
            # Save transcript
            with open('/tmp/wit_transcript.txt', 'w', encoding='utf-8') as f:
                f.write(final_transcript)
            print(f"Transcript saved to /tmp/wit_transcript.txt")
        else:
            print("\n❌ No transcript found in response")
            
            # Show first 500 chars of response for debugging
            print(f"First 500 chars of response:")
            print(response.text[:500])
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up
        os.unlink(wav_path)
        print(f"\nCleaned up temporary file: {wav_path}")

if __name__ == "__main__":
    test_wit_transcription()