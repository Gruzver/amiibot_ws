# amiibot_ws — Workspace ROS2 Humble

Robot diferencial de 4 ruedas (2 motrices + 2 castor) con soporte para simulación (Ignition Gazebo)
y robot real (ODrive + BNO055 + RPLidar). Objetivo a largo plazo: navegación autónoma en entornos
dinámicos con social awareness (paper de investigación).

---

## Hardware

- Computadora: Ubuntu 22.04, ROS2 Humble, GPU RTX 5070
- Motor driver: ODrive (CAN bus, can1)
- IMU: BNO055 (I2C-7, addr 0x28)
- LiDAR: RPLidar A2M8
- Cámara de profundidad: Intel RealSense D435
- Simulador: Ignition Gazebo (Fortress) + Isaac Sim 5.1.0

---

## Paquetes

| Paquete              | Rol                                                       |
|----------------------|-----------------------------------------------------------|
| amiibot_description  | URDF/xacro, mundos Gazebo, meshes, launch de Gazebo       |
| amiibot_controller   | diff_drive_controller, joystick, twist_mux                |
| amiibot_bringup      | Entry points de launch (sim y real), config SLAM          |
| amiibot_navigation   | Nav2, EKF, mapas, launch de navegación                    |
| amiibot_behavior     | Bridge HTTP→ROS2 para sensor de audio                     |
| ros-imu-bno055       | Driver IMU BNO055                                         |

---

## Estado actual — Simulación (Ignition Gazebo)

### ✅ Funcionando
- Gazebo con mundos: empty, small_house, small_warehouse
- diff_drive_controller (teleop con joystick y teclado)
- EKF: fusión odometría + IMU → /odometry/filtered (imu0_differential: true)
- LiDAR RPLidar simulado → /scan
- Cámara de profundidad RealSense D435 simulada → /depth_camera/points
- pointcloud_to_laserscan → /scan_depth (obstacle avoidance local costmap)
- SLAM Toolbox → mapa generado: small_house_map
- Nav2 completo: AMCL + planner + controller + recovery behaviors
- Navegación autónoma a goals con evasión de obstáculos estáticos

### 🔲 Pendiente en Ignition
- Validar evasión de obstáculos dinámicos con /scan_depth
- Personas simuladas con Social Force Model (paquete custom planificado)

---

## Estado actual — Robot real

- En mantenimiento, no disponible para pruebas
- Launch de bringup listo: amiibot_bringup/launch/amiibot_bringup.launch.py

---

## Comandos principales

### Simulación base
```bash
source install/setup.bash
ros2 launch amiibot_bringup amiibot_simulation.launch.py world_name:=small_house
```

### SLAM (generar mapa)
```bash
ros2 launch amiibot_bringup amiibot_slam.launch.py use_sim_time:=true
# Guardar mapa:
ros2 run nav2_map_server map_saver_cli -f src/amiibot_navigation/maps/nombre_mapa
```

### Navegación autónoma
```bash
ros2 launch amiibot_navigation nav2_bringup.launch.py use_sim_time:=true
# Poner 2D Pose Estimate en RViz, luego Nav2 Goal
```

### Robot real
```bash
ros2 launch amiibot_bringup amiibot_bringup.launch.py
```

---

## Flujo de tópicos clave

```
joy/teclado/Nav2 → twist_mux → /amiibot_controller/cmd_vel_unstamped → diff_drive_controller
odom + IMU (/data) → EKF → /odometry/filtered → Nav2
/scan (LiDAR) → Nav2 costmap + SLAM
/depth_camera/points → pointcloud_to_laserscan → /scan_depth → Nav2 local costmap
AMCL + mapa → TF map→odom → Nav2 global planner
```

---

## Parámetros físicos del robot

- Ruedas: radio = 0.0855 m, separación = 0.345 m
- Cámara D435: posición xyz="0.12 0 0.6" en base_link, FOV 87°, rango 0.3-10m
- LiDAR: posición xyz="0.16 0 0.285" en base_link

---

## Plan de desarrollo

### Fase actual — Validación en Ignition Gazebo
1. Validar evasión de obstáculos dinámicos con /scan_depth
2. Implementar simulación de personas con Social Force Model (paquete amiibot_people_sim)

### Siguiente fase — Migración a Isaac Sim 5.1.0
Objetivo: simulación de mayor fidelidad para investigación en social navigation.

**Pendiente antes de migrar:**
- Resolver crash de LiDAR en Isaac Sim (posiblemente parámetros de ray tracing)

**Trabajo de migración:**
1. Importar URDF del robot a Isaac Sim (URDF → USD)
2. Configurar sensores: LiDAR, D435, IMU en Isaac Sim
3. Conectar Nav2 via ROS2 bridge (isaacsim.ros2.bridge)
4. Migrar simulación de personas

### Fase final — Paper: Social Navigation con Human Interaction
Objetivo: robot que navega en entornos con personas con social awareness e interacción.

**Stack planificado:**
- Isaac Sim 5.1.0: simulación fotorrealista + personas animadas
- HuNavSim: Social Force Model para comportamiento de personas
- Nav2 + social costmap layer: evasión de personas con respeto a espacio personal
- RealSense D435: detección de personas en tiempo real
- Agente LLM: comunicación verbal robot-persona para desplazamiento
- Métricas: personal space violations, time-to-goal, success rate vs baselines (DWA-Social, ORCA)

---

## Rama activa: dev
## Repositorio: https://github.com/Gruzver/amiibot_ws
