from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('slam_toolbox'),
                'launch',
                'online_async_launch.py'
            ])
        ]),
        launch_arguments={
            'slam_params_file': PathJoinSubstitution([
                FindPackageShare('amiibot_bringup'),
                'config',
                'amiibot_slam_config.yaml'
            ])
        }.items()
    )

    return LaunchDescription([
        slam_toolbox_launch
    ])