#!/bin/bash
# Spawn a box obstacle in Ignition Gazebo to test dynamic obstacle avoidance.
# Usage: ./scripts/spawn_obstacle.sh [X] [Y]
# Default: 2.0m ahead of the robot origin (x=2.0, y=0.0)
#
# Steps:
#   1. Launch simulation:  ros2 launch amiibot_bringup amiibot_simulation.launch.py world_name:=small_house
#   2. Launch nav2:        ros2 launch amiibot_navigation nav2_bringup.launch.py use_sim_time:=true
#   3. In RViz: set 2D Pose Estimate, then send a Nav2 Goal ~4m ahead (e.g. x=4, y=0)
#   4. While robot is moving, run this script to place box in its path

X=${1:-2.0}
Y=${2:-0.0}
Z=0.75   # half of box height (1.5m tall box)
WORLD="default"
NAME="dynamic_obstacle"

SDF_FILE="$(dirname "$0")/../src/amiibot_description/models/dynamic_obstacle/model.sdf"

if [ ! -f "$SDF_FILE" ]; then
  echo "ERROR: SDF not found at $SDF_FILE"
  exit 1
fi

echo "Spawning obstacle at x=$X y=$Y z=$Z in world '$WORLD'..."
ros2 run ros_gz_sim create \
  -world "$WORLD" \
  -name "$NAME" \
  -x "$X" -y "$Y" -z "$Z" \
  -file "$SDF_FILE"
