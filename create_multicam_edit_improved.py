#!/usr/bin/env python3
"""
Improved multi-camera edit that switches between cameras every 3 seconds using FFmpeg.
This version handles iPhone video formats better and is more efficient.
"""

import subprocess
import os
from pathlib import Path

def get_video_info(video_path):
    """Get video duration and basic info."""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_entries', 'format=duration:stream=codec_type,duration',
        str(video_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
    except Exception as e:
        print(f"Error getting info for {video_path}: {e}")
        return 0

def create_multicam_edit_improved():
    """Create the multi-camera edit using a simpler FFmpeg approach."""
    videos_dir = Path('./videos')

    # Video file paths
    cam1_path = videos_dir / 'Cam1.MOV'
    cam2_path = videos_dir / 'Cam2.MOV'
    cam3_path = videos_dir / 'Cam3.MOV'
    output_path = videos_dir / 'final.mov'

    # Check if all input files exist
    for cam_path in [cam1_path, cam2_path, cam3_path]:
        if not cam_path.exists():
            print(f"Error: {cam_path} not found")
            return False

    # Get durations
    print("Getting video information...")
    durations = [
        get_video_info(cam1_path),
        get_video_info(cam2_path),
        get_video_info(cam3_path)
    ]

    print(f"Cam1 duration: {durations[0]:.2f}s")
    print(f"Cam2 duration: {durations[1]:.2f}s")
    print(f"Cam3 duration: {durations[2]:.2f}s")

    # Find the shortest duration
    min_duration = min(durations)
    switch_interval = 3

    # Calculate total number of 3-second segments we can make
    total_segments = int(min_duration // switch_interval)
    final_duration = total_segments * switch_interval

    print(f"Creating {total_segments} segments of {switch_interval}s each")
    print(f"Final video will be {final_duration:.0f} seconds long")

    # Create a more efficient filter using segment approach
    filter_parts = []

    for i in range(total_segments):
        start_time = i * switch_interval
        camera_index = i % 3  # Cycle through cameras 0, 1, 2

        # Use trim and setpts for each segment
        filter_parts.append(f"[{camera_index}:v]trim=start={start_time}:duration={switch_interval},setpts=PTS-STARTPTS[v{i}];")
        filter_parts.append(f"[{camera_index}:a]atrim=start={start_time}:duration={switch_interval},asetpts=PTS-STARTPTS[a{i}];")

    # Concatenate all video segments
    video_inputs = "".join([f"[v{i}]" for i in range(total_segments)])
    audio_inputs = "".join([f"[a{i}]" for i in range(total_segments)])

    filter_parts.append(f"{video_inputs}concat=n={total_segments}:v=1:a=0[outv];")
    filter_parts.append(f"{audio_inputs}concat=n={total_segments}:v=0:a=1[outa]")

    filter_complex = "".join(filter_parts)

    # Build FFmpeg command with better settings for iPhone videos
    cmd = [
        'ffmpeg',
        '-i', str(cam1_path),
        '-i', str(cam2_path),
        '-i', str(cam3_path),
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', '[outa]',
        '-c:v', 'libx264',     # Use H.264 for compatibility
        '-c:a', 'aac',         # Use AAC for audio
        '-preset', 'fast',     # Faster encoding
        '-crf', '20',          # Good quality
        '-movflags', '+faststart',  # Optimize for streaming
        '-avoid_negative_ts', 'make_zero',  # Handle timing issues
        '-y',                  # Overwrite output file
        str(output_path)
    ]

    print(f"\nCreating multi-camera edit...")
    print(f"Camera switching pattern: Cam1 → Cam2 → Cam3 → Cam1...")
    print("Processing... (this may take a few minutes)")

    try:
        # Run FFmpeg command with less verbose output
        env = os.environ.copy()
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)

        print(f"\n✅ Success! Multi-camera edit saved as: {output_path}")

        # Get final file info
        if output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            final_dur = get_video_info(output_path)
            print(f"📊 Output file size: {file_size:.1f} MB")
            print(f"⏱️  Final duration: {final_dur:.1f} seconds")
            print(f"🎥 Total segments: {total_segments}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error during FFmpeg processing:")
        print(f"stderr: {e.stderr}")
        return False

def main():
    """Main function."""
    print("🎬 Multi-Camera Edit Creator (Improved)")
    print("=" * 50)
    print("📹 Switching between cameras every 3 seconds")
    print("🔄 Camera order: Cam1 → Cam2 → Cam3 → Cam1...")
    print()

    success = create_multicam_edit_improved()

    if success:
        print("\n🎉 Edit complete! You can play final.mov to see the result.")
        print("💡 The video switches cameras every 3 seconds automatically.")
    else:
        print("\n❌ Edit failed. Please check the error messages above.")

if __name__ == "__main__":
    main()