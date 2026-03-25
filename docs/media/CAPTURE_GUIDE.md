# Media Capture Guide

This directory holds the images and GIFs referenced in the README.
Below is the list of files to capture, with instructions for each.

---

## Files needed

### `amiibot_demo.gif` — Hero image (header of README)
**What to capture:** The physical robot, or a side-angle Gazebo view of amiibot moving in `small_house`.
**Ideal content:** Robot navigating autonomously, camera following it.
**Duration:** 8–12 seconds.
**Tool:** Peek (`sudo apt install peek`) or `kazam` for screen recording → convert to GIF with `ffmpeg`.

```bash
# Convert video to GIF (example)
ffmpeg -i demo.mp4 -vf "fps=15,scale=800:-1:flags=lanczos" -c:v gif amiibot_demo.gif
```

---

### `gazebo_simulation.gif` — Simulation overview
**What to capture:** Gazebo window with robot in `small_house`. Drive around with keyboard teleop.
**Ideal content:** Robot moving through corridors, LiDAR scan visible as overlay in RViz.
**Duration:** 10–15 seconds.

**Commands to run first:**
```bash
ros2 launch amiibot_bringup amiibot_simulation.launch.py world_name:=small_house
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/key_vel
```

---

### `nav2_navigation.gif` — Autonomous navigation with dynamic obstacle
**What to capture:** RViz view — robot navigating to a goal, obstacle spawned mid-path, robot replanning around it.
**Ideal content:** Goal marker visible, costmaps visible (local + global), robot path updating after obstacle appears.
**Duration:** 15–20 seconds.

**Commands to run first:**
```bash
ros2 launch amiibot_bringup amiibot_simulation.launch.py world_name:=small_house
ros2 launch amiibot_navigation nav2_bringup.launch.py use_sim_time:=true
# Set 2D Pose Estimate, send a Nav2 Goal, then in a new terminal:
bash scripts/spawn_obstacle.sh
```

---

### `rviz_nav.png` — RViz screenshot with costmaps
**What to capture:** Static screenshot of RViz showing:
- Robot model
- `/scan` laser overlay
- Local costmap (inflation visible)
- Global costmap
- Planned path

**How:** In RViz, ensure both costmaps are added as displays, then `File > Save Image` or use `scrot`.

```bash
scrot docs/media/rviz_nav.png
```

---

### `small_house_world.png` — Gazebo world overview
**What to capture:** Overhead view of the `small_house` world in Gazebo.
**How:** In Gazebo, use the orbit camera (right-click drag) to get a top-down view, then `Edit > Screenshot`.

---

## Recommended tools

| Task | Tool | Install |
|------|------|---------|
| Screen recording to GIF | Peek | `sudo apt install peek` |
| Screen recording to video | Kazam | `sudo apt install kazam` |
| Video → GIF conversion | ffmpeg | `sudo apt install ffmpeg` |
| Screenshot | scrot | `sudo apt install scrot` |

---

## README placeholder comments

Once you have the files, uncomment the corresponding lines in `README.md`:

```markdown
<!-- Replace with actual robot photo or demo GIF -->
<!-- ![amiibot demo](docs/media/amiibot_demo.gif) -->
```

Simply remove the `<!--` and `-->` wrapping each image line.
