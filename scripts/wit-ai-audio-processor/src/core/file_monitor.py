"""
File system monitor for audio files
"""

import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class AudioFileHandler(FileSystemEventHandler):
    """Handle new audio file events"""
    
    def __init__(self, processor, incoming_dir: Path, processed_dir: Path):
        self.processor = processor
        self.incoming_dir = incoming_dir
        self.processed_dir = processed_dir
        self.processed_files = set()
        
        # Load already processed files
        self.load_processed_files()
    
    def load_processed_files(self):
        """Load list of already processed files"""
        try:
            if self.processed_dir.exists():
                for file in self.processed_dir.iterdir():
                    if file.is_file():
                        self.processed_files.add(file.name)
            logger.info(f"Loaded {len(self.processed_files)} previously processed files")
        except Exception as e:
            logger.error(f"Error loading processed files: {e}")
    
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self.process_file(Path(event.src_path))
    
    def on_moved(self, event):
        """Handle file move events"""
        if not event.is_directory:
            self.process_file(Path(event.dest_path))
    
    def process_file(self, filepath: Path):
        """Process a new audio file"""
        # Check if file is in incoming directory
        if filepath.parent != self.incoming_dir:
            return
        
        # Check if already processed
        if filepath.name in self.processed_files:
            logger.debug(f"Skipping already processed file: {filepath.name}")
            return
        
        # Wait for file to be fully written
        time.sleep(0.5)
        
        # Check file size
        try:
            if filepath.stat().st_size == 0:
                logger.warning(f"Empty file: {filepath.name}")
                return
        except OSError:
            logger.warning(f"File not accessible yet: {filepath.name}")
            return
        
        # Check file extension
        valid_extensions = {'.ogg', '.mp3', '.wav', '.m4a', '.flac', '.opus'}
        if filepath.suffix.lower() not in valid_extensions:
            logger.debug(f"Skipping non-audio file: {filepath.name}")
            return
        
        # Process the file
        logger.info(f"New audio file detected: {filepath.name}")
        success = self.processor.process_audio_file(filepath)
        
        if success:
            self.processed_files.add(filepath.name)
            logger.info(f"Successfully processed: {filepath.name}")
        else:
            logger.error(f"Failed to process: {filepath.name}")

class AudioFileMonitor:
    """Monitor directory for new audio files"""
    
    def __init__(self, processor, incoming_dir: Path, processed_dir: Path):
        self.processor = processor
        self.incoming_dir = incoming_dir
        self.processed_dir = processed_dir
        self.observer = None
        self.event_handler = None
    
    def start(self):
        """Start monitoring directory"""
        # Create event handler
        self.event_handler = AudioFileHandler(
            processor=self.processor,
            incoming_dir=self.incoming_dir,
            processed_dir=self.processed_dir
        )
        
        # Create observer
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(self.incoming_dir),
            recursive=False
        )
        
        # Start observer
        self.observer.start()
        logger.info(f"Started monitoring: {self.incoming_dir}")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            self.stop()
    
    def stop(self):
        """Stop monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped monitoring")