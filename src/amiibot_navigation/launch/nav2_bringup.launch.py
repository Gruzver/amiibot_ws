from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    use_sim_time_arg = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='false',
        description='Use simulation time (true for Gazebo/sim, false for real robot)'
    )

    map_arg = DeclareLaunchArgument(
        name='map',
        default_value=PathJoinSubstitution(
            [FindPackageShare("amiibot_navigation"), "maps", "small_house_map.yaml"]
        ),
        description='Full path to map yaml file'
    )

    params_file_arg = DeclareLaunchArgument(
        name='params_file',
        default_value=PathJoinSubstitution(
            [FindPackageShare("amiibot_navigation"), "config", "nav2_params.yaml"]
        ),
        description='Full path to nav2 params yaml file'
    )

    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        use_sim_time_arg,
        map_arg,
        params_file_arg,

        # --- LOCALIZATION (AMCL + Map Server) ---
        # Esto publica el TF map -> odom
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_nav2_bringup, 'launch', 'localization_launch.py')
            ),
            launch_arguments={
                'map': LaunchConfiguration('map'),
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': params_file,
                'autostart': 'True',     # <--- CRÍTICO: Arranca el ciclo de vida automáticamente
                'use_lifecycle_mgr': 'False' # localization_launch ya trae su propio manager, esto evita conflictos si usas versiones antiguas
            }.items()
        ),

        # --- NAVIGATION (Planner + Controller + BT + Recoveries) ---
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
            ),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': params_file,
                'autostart': 'True',     # <--- CRÍTICO
                'use_lifecycle_mgr': 'False'
            }.items()
        )
    ])