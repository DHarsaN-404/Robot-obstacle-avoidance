# ROS 2 Smart Obstacle Avoidance 🤖

![ROS 2](https://img.shields.io/badge/ROS_2-Humble-3490dc?style=for-the-badge&logo=ros&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-3776ab?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-TurtleBot3-orange?style=for-the-badge&logo=gazebo&logoColor=white)

> **Autonomous navigation stack implementation for TurtleBot3 using ROS 2 Humble. Features reactive obstacle avoidance, dynamic velocity scaling, and emergency recovery behaviors.**

---

## 📖 Overview

![turtle](https://github.com/user-attachments/assets/c3db2069-a275-4ed0-9370-d90c9bb4cace)

The `smart_avoidance` node is designed to navigate a robot through cluttered environments autonomously. Unlike rigid deterministic algorithms that often get trapped in repetitive loops (wall-following), this project implements a **Stochastic Finite State Machine (FSM)** that enables the robot to:

1.  **Cruise & Wander:** Adjusts velocity dynamically based on free space while applying slight random drifts to mimic natural exploration behavior.
2.  **Resolve Symmetry:** Uses a probabilistic "coin-flip" logic when facing symmetric obstacles (e.g., pillars) to break deadlocks and force a decision.
3.  **Seek Gaps:** Utilizes a focused "Tunnel Vision" approach to identify and confidently enter narrow passages between obstacles.
4.  **Recover Safely:** Triggers a randomized reverse maneuver to reorient itself if trapped or if an object appears suddenly.

---

## 🚀 Key Features

- **🏎️ Adaptive Cruise Control (ACC):**
  The robot accelerates in open spaces (up to `0.45 m/s`) and automatically decelerates as it approaches obstacles to ensure safer maneuvering.
- **🎲 Random Exploration Strategy:**
  Unlike deterministic algorithms that get stuck following walls, this node implements a **"Wander Behavior"**. It applies random angular drifts in open spaces and uses a stochastic "coin-flip" decision when facing symmetric obstacles to encourage entering complex areas (like pillar fields).
- **🛡️ Emergency Reverse Gear:**
  Safety-critical feature: If an obstacle breaches the collision threshold (< 0.25m), the robot halts and reverses to prevent impact before attempting to turn.
- **📉 Signal Noise Filtering:**
  Implements a minimum-distance filter to handle invalid sensor readings (`inf`, `NaN`) and prevent jittery motion.

---

## 🛠️ System Architecture

| Attribute              | Details                            |
| :--------------------- | :--------------------------------- |
| **Node Name**          | `smart_avoidance`                  |
| **Package Name**       | `my_bot_pkg`                       |
| **Language**           | Python 3                           |
| **Input (Subscriber)** | `/scan` (`sensor_msgs/LaserScan`)  |
| **Output (Publisher)** | `/cmd_vel` (`geometry_msgs/Twist`) |

---

## 🧠 Navigation Logic (State Machine)

The robot's behavior is governed by the distance to the nearest object in the **Front Sector** (+/- 20°).

| State            | Front Distance     | Behavior    | Action                                                              |
| :--------------- | :----------------- | :---------- | :------------------------------------------------------------------ |
| **🔴 EMERGENCY** | `< 0.25 m`         | **Reverse** | Linear: `-0.15` m/s                                                 |
| **🟡 AVOID**     | `0.25 m` - `0.7 m` | **Turn**    | Linear: `0.05` m/s (Crawl)<br>Angular: `+/- 0.8` rad/s (Smart Turn) |
| **🟢 CRUISE**    | `> 0.7 m`          | **Forward** | Linear: `Variable` (Max 0.45 m/s)<br>Angular: `0.0` rad/s           |

---

## ⚙️ Installation & Setup

### Prerequisites

- Ubuntu 22.04 LTS
- ROS 2 Humble
- TurtleBot3 Simulations

### Installation

You can set up this project by cloning the repository directly into your workspace.

1. **Go to your workspace src folder**
   Change 'ros2_ws' and 'src' if your workspace has a different name

```bash
cd ~/ros2_ws/src
```

2. **Clone the repository**

```bash
git clone https://github.com/Hesyitena/ros2-smart-obstacle-avoidance.git
```

To install the required simulation packages:

```bash
sudo apt update
sudo apt install ros-humble-turtlebot3-gazebo
```

### Build the package

After cloning, you must build the workspace to register the new package.

```bash
cd ~/ros2_ws
colcon build --packages-select my_bot_pkg
source install/setup.bash
```

## 🕹️ Usage Guide

### Step 1: Launch Simulation

Open a new terminal to load the Gazebo world.

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### Step 2: Run the Navigation Node

Open a second terminal to start the autonomous logic.

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run my_bot_pkg gerak_otomatis
```

## ❓ Troubleshooting

- **Issue:** `Package 'my_bot_pkg' not found`
  - **Fix:** Ensure you are in the root workspace folder (`~/ros2_ws`) and have run `source install/setup.bash`
- **Issue:** Robot spins in place.
  - **FIx:** Check if Gazebo is fully loaded. If the LiDAR data is `inf` everywhere, the robot defaults to safe mode.
- **Issue:** `ModuleNotFoundError: No module named 'rclpy'`
  - **Fix:** Make sure you have sourced ROS 2 main setup: `source /opt/ros/humble/setup.bash`.

## 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

### Note: This project is for educational and simulation purposes.
