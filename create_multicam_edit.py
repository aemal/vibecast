#!/usr/bin/env python3
"""
Create a multi-camera edit that switches between cameras every 3 seconds using FFmpeg.
This script processes Cam1.MOV, Cam2.MOV, and Cam3.MOV to create final.mov.
"""

import subprocess
import os
from pathlib import Path

def get_video_duration(video_path):
    """Get the duration of a video file in seconds."""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-show_entries', 'format=duration',
        '-of', 'csv=p=0',
        str(video_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting duration for {video_path}: {e}")
        return 0

def create_filter_complex(durations, switch_interval=3):
    """Create the FFmpeg filter complex for switching between cameras."""
    # Find the shortest duration to determine total edit length
    min_duration = min(durations)

    # Calculate how many complete switch cycles we can fit
    total_switches = int(min_duration // switch_interval)

    # Create the filter complex
    filter_parts = []

    # For each switch interval
    for i in range(total_switches):
        start_time = i * switch_interval
        camera_index = i % 3  # Cycle through cameras 0, 1, 2

        # Add trim filter for this segment
        filter_parts.append(f"[{camera_index}:v]trim=start={start_time}:duration={switch_interval},setpts=PTS-STARTPTS[v{i}];")
        filter_parts.append(f"[{camera_index}:a]atrim=start={start_time}:duration={switch_interval},asetpts=PTS-STARTPTS[a{i}];")

    # Concatenate all segments
    video_inputs = "".join([f"[v{i}]" for i in range(total_switches)])
    audio_inputs = "".join([f"[a{i}]" for i in range(total_switches)])

    filter_parts.append(f"{video_inputs}concat=n={total_switches}:v=1:a=0[outv];")
    filter_parts.append(f"{audio_inputs}concat=n={total_switches}:v=0:a=1[outa]")

    return "".join(filter_parts), total_switches * switch_interval

def create_multicam_edit():
    """Create the multi-camera edit using FFmpeg."""
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
    print("Getting video durations...")
    durations = [
        get_video_duration(cam1_path),
        get_video_duration(cam2_path),
        get_video_duration(cam3_path)
    ]

    print(f"Cam1 duration: {durations[0]:.2f}s")
    print(f"Cam2 duration: {durations[1]:.2f}s")
    print(f"Cam3 duration: {durations[2]:.2f}s")

    # Create filter complex
    switch_interval = 3
    filter_complex, final_duration = create_filter_complex(durations, switch_interval)

    print(f"Final video will be {final_duration:.2f} seconds long")
    print(f"Switching every {switch_interval} seconds between cameras")

    # Build FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', str(cam1_path),
        '-i', str(cam2_path),
        '-i', str(cam3_path),
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', '[outa]',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-preset', 'medium',
        '-crf', '23',
        '-y',  # Overwrite output file
        str(output_path)
    ]

    print("\nStarting FFmpeg processing...")
    print("This may take a few minutes depending on video size...")

    try:
        # Run FFmpeg command
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\nSuccess! Multi-camera edit saved as: {output_path}")

        # Get final file size
        if output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            print(f"Output file size: {file_size:.1f} MB")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error during FFmpeg processing: {e}")
        return False

def main():
    """Main function."""
    print("Multi-Camera Edit Creator")
    print("=" * 40)
    print("Switching between cameras every 3 seconds")
    print("Camera order: Cam1 → Cam2 → Cam3 → Cam1 → ...")
    print()

    success = create_multicam_edit()

    if success:
        print("\nEdit complete! You can play final.mov to see the result.")
    else:
        print("\nEdit failed. Please check the error messages above.")

if __name__ == "__main__":
    main()