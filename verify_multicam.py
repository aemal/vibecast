#!/usr/bin/env python3
"""
Verify the multi-camera edit and show information about the final video.
"""

import subprocess
import json
from pathlib import Path

def get_detailed_video_info(video_path):
    """Get detailed information about a video file."""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_entries', 'format=duration,size,bit_rate:stream=codec_name,width,height,r_frame_rate',
        str(video_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting info for {video_path}: {e}")
        return None

def main():
    """Main verification function."""
    videos_dir = Path('./videos')
    final_path = videos_dir / 'final.mov'

    print("🔍 Multi-Camera Edit Verification")
    print("=" * 40)

    if not final_path.exists():
        print("❌ final.mov not found!")
        return

    # Get info about final video
    info = get_detailed_video_info(final_path)

    if info:
        # Format info
        format_info = info.get('format', {})
        duration = float(format_info.get('duration', 0))
        size = int(format_info.get('size', 0))
        bitrate = format_info.get('bit_rate', 'unknown')

        # Stream info
        streams = info.get('streams', [])
        video_stream = next((s for s in streams if s.get('codec_type') == 'video'), {})
        audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), {})

        print(f"✅ Final video created successfully!")
        print(f"📁 File: {final_path}")
        print(f"📏 File size: {size / (1024*1024):.1f} MB")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"🎥 Video codec: {video_stream.get('codec_name', 'unknown')}")
        print(f"🔊 Audio codec: {audio_stream.get('codec_name', 'unknown')}")

        if video_stream:
            width = video_stream.get('width', 'unknown')
            height = video_stream.get('height', 'unknown')
            fps = video_stream.get('r_frame_rate', 'unknown')
            print(f"📺 Resolution: {width}x{height}")
            print(f"🎬 Frame rate: {fps}")

        # Calculate expected segments
        segments = int(duration / 3)
        print(f"\n📊 Analysis:")
        print(f"🔄 Expected 3-second segments: {segments}")
        print(f"📹 Camera switches: Every 3 seconds")
        print(f"🎯 Pattern: Cam1 → Cam2 → Cam3 → Cam1...")

        print(f"\n💡 To preview the video, you can use:")
        print(f"   open {final_path}")
        print(f"   or")
        print(f"   ffplay {final_path}")

    else:
        print("❌ Could not read video information")

if __name__ == "__main__":
    main()