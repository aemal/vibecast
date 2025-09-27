#!/usr/bin/env python3
"""
Simple multi-camera edit using a straightforward FFmpeg approach.
Creates 3-second segments from each camera and concatenates them.
"""

import subprocess
import os
from pathlib import Path

def create_simple_multicam():
    """Create multi-camera edit with simple segment approach."""
    videos_dir = Path('./videos')

    # Input files
    cam_files = ['Cam1.MOV', 'Cam2.MOV', 'Cam3.MOV']
    output_file = 'final.mov'

    print("🎬 Simple Multi-Camera Editor")
    print("=" * 40)

    # Remove existing final.mov
    final_path = videos_dir / output_file
    if final_path.exists():
        final_path.unlink()
        print("🗑️  Removed existing final.mov")

    # Create segments list file for FFmpeg concat
    segments_file = videos_dir / 'segments.txt'

    # We'll create 29 segments (87 seconds total) - this fits within all videos
    total_segments = 29  # Each camera appears ~10 times
    segment_duration = 3

    print(f"📹 Creating {total_segments} segments of {segment_duration}s each")
    print("🔄 Pattern: Cam1 → Cam2 → Cam3 → Cam1...")

    # Create individual segment files first
    segment_files = []

    for i in range(total_segments):
        camera_index = i % 3
        start_time = i * segment_duration  # Start from the same time for each cycle

        cam_file = cam_files[camera_index]
        segment_file = f"segment_{i:03d}_cam{camera_index + 1}.mov"
        segment_path = videos_dir / segment_file

        print(f"Creating segment {i+1}/{total_segments}: {segment_file} (from {cam_file} at {start_time}s)")

        # Create individual segment
        cmd = [
            'ffmpeg',
            '-i', str(videos_dir / cam_file),
            '-ss', str(start_time),
            '-t', str(segment_duration),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-avoid_negative_ts', 'make_zero',
            '-y',
            str(segment_path)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            segment_files.append(segment_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating segment {i}: {e}")
            return False

    print(f"\n✅ Created {len(segment_files)} segments")

    # Create concat file list
    with open(segments_file, 'w') as f:
        for segment_file in segment_files:
            f.write(f"file '{segment_file}'\n")

    print("📝 Created segments list file")

    # Concatenate all segments
    print("🔗 Concatenating segments into final.mov...")

    concat_cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(segments_file),
        '-c', 'copy',
        '-y',
        str(final_path)
    ]

    try:
        subprocess.run(concat_cmd, check=True, capture_output=True)
        print("✅ Concatenation successful!")

        # Clean up segment files
        print("🧹 Cleaning up temporary files...")
        for segment_file in segment_files:
            (videos_dir / segment_file).unlink()
        segments_file.unlink()

        # Show final result
        if final_path.exists():
            file_size = final_path.stat().st_size / (1024 * 1024)
            print(f"\n🎉 SUCCESS!")
            print(f"📁 Output: {final_path}")
            print(f"📏 Size: {file_size:.1f} MB")
            print(f"⏱️  Duration: ~{total_segments * segment_duration} seconds")
            print(f"🎥 Segments: {total_segments} × {segment_duration}s each")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error during concatenation: {e}")
        return False

if __name__ == "__main__":
    success = create_simple_multicam()

    if success:
        print("\n💡 You can now play final.mov to see the multi-camera edit!")
        print("   The video switches between cameras every 3 seconds.")
    else:
        print("\n❌ Failed to create multi-camera edit.")