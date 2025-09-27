#!/usr/bin/env python3
"""
Extract UTC timestamps from video files using FFmpeg.
This script processes all video files in the ./videos folder and extracts their creation timestamps.
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

def get_video_metadata(video_path):
    """Extract metadata from video file using ffprobe."""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {video_path}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing metadata for {video_path}: {e}")
        return None

def extract_creation_time(metadata):
    """Extract creation time from video metadata."""
    if not metadata:
        return None

    # Try different metadata fields where creation time might be stored
    creation_time_fields = [
        'creation_time',
        'date',
        'datetime',
        'com.apple.quicktime.creationdate'
    ]

    # Check format tags first
    if 'format' in metadata and 'tags' in metadata['format']:
        tags = metadata['format']['tags']
        for field in creation_time_fields:
            if field in tags:
                return tags[field]

    # Check stream tags
    if 'streams' in metadata:
        for stream in metadata['streams']:
            if 'tags' in stream:
                tags = stream['tags']
                for field in creation_time_fields:
                    if field in tags:
                        return tags[field]

    return None

def format_timestamp(timestamp_str):
    """Format timestamp string to a readable UTC format."""
    if not timestamp_str:
        return "No timestamp found"

    try:
        # Try parsing common timestamp formats
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO format with microseconds
            '%Y-%m-%dT%H:%M:%SZ',     # ISO format without microseconds
            '%Y-%m-%d %H:%M:%S',      # Simple format
            '%Y:%m:%d %H:%M:%S',      # EXIF-style format
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except ValueError:
                continue

        # If no format matches, return as-is
        return f"{timestamp_str} (raw format)"

    except Exception as e:
        return f"Error parsing timestamp: {e}"

def main():
    """Main function to process all videos in the videos folder."""
    videos_dir = Path('./videos')

    if not videos_dir.exists():
        print("Error: ./videos directory not found")
        return

    # Common video file extensions
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}

    # Find all video files
    video_files = []
    for file_path in videos_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in video_extensions:
            video_files.append(file_path)

    if not video_files:
        print("No video files found in ./videos directory")
        return

    print(f"Found {len(video_files)} video file(s) in ./videos directory")
    print("=" * 60)

    # Process each video file
    for video_file in sorted(video_files):
        print(f"\nProcessing: {video_file.name}")

        # Get metadata
        metadata = get_video_metadata(str(video_file))

        # Extract creation time
        creation_time = extract_creation_time(metadata)

        # Format and display
        formatted_time = format_timestamp(creation_time)
        print(f"Creation Time: {formatted_time}")

        if creation_time:
            print(f"Raw Timestamp: {creation_time}")

if __name__ == "__main__":
    main()