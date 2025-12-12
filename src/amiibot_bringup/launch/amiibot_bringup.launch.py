import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    
    # --- RUTAS ---
    pkg_amiibot_bringup = get_package_share_directory('amiibot_bringup')
    pkg_rplidar_ros = get_package_share_directory('rplidar_ros')
    pkg_amiibot_navigation = get_package_share_directory('amiibot_navigation')

    # --- DEFINICIÓN DE NODOS Y LAUNCHES ---

    # 1. ODrive (Motores)
    # Asumimos que el CAN ya está listo gracias al servicio systemd
    odrive_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_amiibot_bringup, 'launch', 'amiibot_base_odrive.launch.py')
        )
    )

    # 2. IMU (BNO055)
    imu_node = Node(
        package='imu_bno055',
        executable='bno055_i2c_node',
        name='bno055_node',
        output='screen',
        parameters=[{
            'device': '/dev/i2c-7',
            'address': 0x28
        }]
    )

    # 3. Lidar (Solo driver, sin view)
    # Usamos 'rplidar_a2m8_launch.py' como pediste.
    # Nota: A veces este archivo se llama 'rplidar.launch.py' o 'sllidar_a2m8_launch.py' 
    # dependiendo de la versión del paquete instalada. Verifica el nombre en tu carpeta.
    rplidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rplidar_ros, 'launch', 'rplidar_a2m8_launch.py')
        )
    )

    # 4. EKF (Odometría filtrada)
    ekf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_amiibot_navigation, 'launch', 'ekf.launch.py')
        )
    )

    # --- SECUENCIA DE INICIO (DELAYS) ---

    # A. Iniciamos Lidar con un pequeño retraso (2s) para no saturar el USB
    # al mismo tiempo que arranca el IMU y la CPU sube de carga.
    delayed_rplidar = TimerAction(
        period=2.0,
        actions=[
            LogInfo(msg="--- Iniciando Lidar (2s delay) ---"),
            rplidar_launch
        ]
    )

    # B. Iniciamos EKF al final (5s)
    # Esto es CRÍTICO: El EKF necesita recibir datos de Odom (ODrive) y Imu 
    # antes de empezar a calcular, si no, da error de "TF extrapolation".
    delayed_ekf = TimerAction(
        period=5.0,
        actions=[
            LogInfo(msg="--- Sensores listos. Iniciando EKF (5s delay) ---"),
            ekf_launch
        ]
    )

    return LaunchDescription([
        odrive_launch,      # Inicia en t=0
        imu_node,           # Inicia en t=0
        delayed_rplidar,    # Inicia en t=2
        delayed_ekf         # Inicia en t=5
    ])