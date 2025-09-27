#!/usr/bin/env python3
"""
Fast multi-camera edit - creates just the first few switches to demonstrate.
"""

import subprocess
from pathlib import Path

def create_demo_multicam():
    """Create a short demo showing camera switching."""
    videos_dir = Path('./videos')
    output_file = videos_dir / 'final.mov'

    print("🎬 Fast Multi-Camera Demo")
    print("Creating 15-second demo (5 switches × 3 seconds each)")

    # Remove existing file
    if output_file.exists():
        output_file.unlink()

    # Create just 5 segments for a quick demo
    filter_complex = (
        # Cam1: 0-3s
        "[0:v]trim=start=0:duration=3,setpts=PTS-STARTPTS[v0];"
        "[0:a]atrim=start=0:duration=3,asetpts=PTS-STARTPTS[a0];"
        # Cam2: 0-3s
        "[1:v]trim=start=0:duration=3,setpts=PTS-STARTPTS[v1];"
        "[1:a]atrim=start=0:duration=3,asetpts=PTS-STARTPTS[a1];"
        # Cam3: 0-3s
        "[2:v]trim=start=0:duration=3,setpts=PTS-STARTPTS[v2];"
        "[2:a]atrim=start=0:duration=3,asetpts=PTS-STARTPTS[a2];"
        # Cam1: 3-6s
        "[0:v]trim=start=3:duration=3,setpts=PTS-STARTPTS[v3];"
        "[0:a]atrim=start=3:duration=3,asetpts=PTS-STARTPTS[a3];"
        # Cam2: 3-6s
        "[1:v]trim=start=3:duration=3,setpts=PTS-STARTPTS[v4];"
        "[1:a]atrim=start=3:duration=3,asetpts=PTS-STARTPTS[a4];"
        # Concatenate: Cam1→Cam2→Cam3→Cam1→Cam2
        "[v0][a0][v1][a1][v2][a2][v3][a3][v4][a4]concat=n=5:v=1:a=1[outv][outa]"
    )

    cmd = [
        'ffmpeg',
        '-i', str(videos_dir / 'Cam1.MOV'),
        '-i', str(videos_dir / 'Cam2.MOV'),
        '-i', str(videos_dir / 'Cam3.MOV'),
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', '[outa]',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-preset', 'ultrafast',
        '-y',
        str(output_file)
    ]

    try:
        print("⚡ Processing... (this should be quick)")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"✅ Success! Created final.mov ({file_size:.1f} MB)")
        print("📹 Demo shows: Cam1→Cam2→Cam3→Cam1→Cam2 (15 seconds total)")
        print("🎥 Each camera shows for 3 seconds")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Details: {e.stderr}")
        return False

if __name__ == "__main__":
    create_demo_multicam()