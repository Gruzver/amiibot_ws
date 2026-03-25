# amiibot

**Autonomous differential-drive robot for social navigation research**

[![ROS2 Humble](https://img.shields.io/badge/ROS2-Humble-blue?logo=ros)](https://docs.ros.org/en/humble/)
[![Ubuntu 22.04](https://img.shields.io/badge/Ubuntu-22.04-orange?logo=ubuntu)](https://ubuntu.com/)
[![Ignition Gazebo](https://img.shields.io/badge/Simulator-Ignition%20Gazebo-green)](https://gazebosim.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<!-- Replace with actual robot photo or demo GIF -->
<!-- ![amiibot demo](docs/media/amiibot_demo.gif) -->

---

## Overview

**amiibot** is a 4-wheel differential-drive robot (2 actuated + 2 castor) built for research in autonomous navigation and human-robot interaction. The platform supports a full simulation workflow in **Ignition Gazebo** and deployment on real hardware (**ODrive + RPLidar + RealSense D435**).

The long-term research goal is social navigation in dynamic human environments, targeting a publication on human-aware robot motion planning.

---

## Features

- **Dual mode**: identical ROS2 interface in simulation (Ignition Gazebo Fortress) and on real hardware
- **Full Nav2 stack**: AMCL localization, NavFn global planner, DWB local controller, recovery behaviors
- **Sensor fusion**: Extended Kalman Filter (odometry + IMU) via `robot_localization`
- **Dynamic obstacle avoidance**: RealSense D435 point cloud → `pointcloud_to_laserscan` → Nav2 local costmap
- **SLAM mapping**: SLAM Toolbox for autonomous map generation
- **Flexible teleoperation**: joystick and keyboard via `twist_mux` priority arbitration
- **Multiple simulation environments**: empty, residential (small_house), warehouse (small_warehouse)

<!-- Replace with simulation demo GIF -->
<!-- ![Gazebo simulation](docs/media/gazebo_simulation.gif) -->

---

## Hardware

| Component         | Model            | Interface     | ROS2 Topic                      |
|-------------------|------------------|---------------|----------------------------------|
| Motor driver      | ODrive v3.6      | CAN bus (can1)| `/amiibot_controller/cmd_vel_unstamped` |
| IMU               | BNO055           | I2C-7 (0x28)  | `/data`                          |
| 2D LiDAR          | RPLidar A2M8     | USB           | `/scan`                          |
| Depth camera      | Intel RealSense D435 | USB 3.0   | `/depth_camera/points`           |
| Computer          | Ubuntu 22.04 / RTX 5070 | —      | —                                |

**Physical parameters:**
- Wheel radius: `0.0855 m` · Wheel separation: `0.345 m`
- LiDAR mount: `xyz = [0.16, 0, 0.285]` relative to `base_link`
- D435 mount: `xyz = [0.12, 0, 0.60]` relative to `base_link`, FOV 87°, range 0.3–10 m

---

## Package Architecture

| Package                | Type          | Role                                                        |
|------------------------|---------------|-------------------------------------------------------------|
| `amiibot_description`  | ament_cmake   | URDF/xacro, Gazebo worlds, meshes, RViz config              |
| `amiibot_controller`   | ament_cmake   | `diff_drive_controller`, joystick teleop, `twist_mux`       |
| `amiibot_bringup`      | ament_cmake   | Launch entry points for simulation and real robot           |
| `amiibot_navigation`   | ament_python  | Nav2 stack, EKF, pre-built maps, navigation launch files    |
| `amiibot_behavior`     | ament_python  | HTTP → ROS2 bridge for audio sensor integration             |
| `ros-imu-bno055`       | ament_cmake   | BNO055 IMU driver                                           |

### Topic Flow

```
joy / keyboard / Nav2 Goal
        │
        ▼
    twist_mux
        │
        ▼
/amiibot_controller/cmd_vel_unstamped
        │
        ▼
diff_drive_controller ──► /amiibot_controller/odom ──►┐
                                                        │
BNO055 ──────────────────────────────► /data ──────────┤
                                                        ▼
                                                   EKF (robot_localization)
                                                        │
                                                        ▼
                                              /odometry/filtered
                                                        │
                                                        ▼
RPLidar ──────────────────────────────► /scan ─────► Nav2 (costmap + AMCL)
                                                        ▲
RealSense D435 ──► /depth_camera/points                 │
        │                                               │
        ▼                                               │
pointcloud_to_laserscan ──────────────► /scan_depth ───┘
```

---

## Installation

### Prerequisites

```bash
# ROS2 Humble — https://docs.ros.org/en/humble/Installation.html
sudo apt install -y \
  ros-humble-nav2-bringup \
  ros-humble-robot-localization \
  ros-humble-slam-toolbox \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-twist-mux \
  ros-humble-pointcloud-to-laserscan \
  ros-humble-joint-state-publisher-gui \
  ros-humble-xacro

# Ignition Gazebo Fortress
sudo apt install -y ros-humble-ros-ign-bridge ros-humble-ign-ros2-control
```

### Clone and build

```bash
mkdir -p ~/amiibot_ws/src
cd ~/amiibot_ws/src
git clone https://github.com/Gruzver/amiibot_ws.git .

cd ~/amiibot_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

---

## Quick Start

> All commands assume `source install/setup.bash` has been run.

### 1 — Simulation (Ignition Gazebo)

```bash
ros2 launch amiibot_bringup amiibot_simulation.launch.py world_name:=small_house
```

Available worlds: `empty` · `small_house` · `small_warehouse`

<!-- ![Gazebo small_house](docs/media/small_house_world.png) -->

### 2 — Teleoperation

Keyboard control (in a new terminal):
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args --remap cmd_vel:=/key_vel
```

### 3 — SLAM: Build a Map

```bash
ros2 launch amiibot_bringup amiibot_slam.launch.py use_sim_time:=true
```

Save the map when done:
```bash
ros2 run nav2_map_server map_saver_cli -f src/amiibot_navigation/maps/my_map
```

### 4 — Autonomous Navigation

```bash
ros2 launch amiibot_navigation nav2_bringup.launch.py use_sim_time:=true
```

1. In RViz: click **2D Pose Estimate** and click the robot's initial position on the map
2. Click **Nav2 Goal** and click a destination — the robot plans and navigates autonomously

<!-- ![Nav2 navigation with dynamic obstacle avoidance](docs/media/nav2_navigation.gif) -->

<!-- ![RViz costmaps](docs/media/rviz_nav.png) -->

### 5 — Real Robot

```bash
ros2 launch amiibot_bringup amiibot_bringup.launch.py
```

> **Note:** Real robot is currently in maintenance. ODrive CAN interface must be configured on `can1` before launching.

---

## Simulation Worlds

| World               | Description                                  | Use case                    |
|---------------------|----------------------------------------------|-----------------------------|
| `empty`             | Flat plane, no obstacles                     | Controller tuning, EKF validation |
| `small_house`       | Furnished residential environment             | SLAM, Nav2, obstacle avoidance |
| `small_warehouse`   | Industrial warehouse with shelving            | Navigation in cluttered spaces |

---

## Development Roadmap

### Phase 1 — Ignition Gazebo Validation ✅
- [x] Full Nav2 stack with AMCL + EKF
- [x] Dynamic obstacle avoidance via RealSense D435 + `pointcloud_to_laserscan`
- [ ] Simulated people with Social Force Model (`amiibot_people_sim`)

### Phase 2 — Migration to Isaac Sim 5.1.0
- [ ] Resolve LiDAR crash (ray tracing parameters, RTX 5070 Blackwell)
- [ ] Import URDF → USD, configure sensors in Isaac Sim
- [ ] Connect Nav2 via `isaacsim.ros2.bridge`
- [ ] Integrate HuNavSim for realistic pedestrian simulation

### Phase 3 — Research: Social Navigation with Human Interaction
- [ ] Social costmap layer (personal space zones)
- [ ] HuNavSim Social Force Model for pedestrian behavior
- [ ] Real-time person detection with RealSense D435
- [ ] LLM-based verbal interaction for obstacle clearing
- [ ] Benchmarks vs. DWA-Social, ORCA, CADRL
- [ ] Metrics: personal space violations, time-to-goal, success rate

---

## Research Context

This platform is developed as part of a master's thesis research project on **socially-aware robot navigation**. The goal is to enable robots to navigate safely and naturally in environments shared with humans — respecting personal space, reacting to pedestrian intent, and communicating when needed.

Target venue: IEEE / robotics conference. The platform serves as the testbed for comparing navigation algorithms under social constraints.

---

## Repository Structure

```
amiibot_ws/
├── src/
│   ├── amiibot_description/   # URDF, worlds, meshes
│   ├── amiibot_controller/    # diff_drive, teleop, twist_mux
│   ├── amiibot_bringup/       # launch entry points
│   ├── amiibot_navigation/    # Nav2, EKF, maps
│   ├── amiibot_behavior/      # audio sensor bridge
│   └── ros-imu-bno055/        # BNO055 driver
├── scripts/
│   └── spawn_obstacle.sh      # spawn dynamic obstacles for testing
├── docs/
│   └── media/                 # screenshots and demo GIFs
└── README.md
```

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- [Nav2](https://github.com/ros-planning/navigation2) — navigation stack
- [linorobot2](https://github.com/linorobot/linorobot2) — reference architecture for ROS2 differential-drive robots
- [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox) — mapping
- [robot_localization](https://github.com/cra-ros-pkg/robot_localization) — EKF sensor fusion
