import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    world_name_arg = DeclareLaunchArgument(
        "world_name",
        default_value="empty",
        description="World to load: empty, small_house, small_warehouse"
    )

    gazebo = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("amiibot_description"),
            "launch",
            "gazebo.launch.py"
        ),
        launch_arguments={"world_name": LaunchConfiguration("world_name")}.items()
    )

    controller = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("amiibot_controller"),
            "launch",
            "controller.launch.py"
        ),
        launch_arguments={"use_sim_time": "True"}.items()
    )

    joystick = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("amiibot_controller"),
            "launch",
            "joystick_teleop.launch.py"
        ),
        launch_arguments={"use_sim_time": "True"}.items()
    )

    ekf = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("amiibot_navigation"),
            "launch",
            "ekf.launch.py"
        ),
        launch_arguments={"use_sim_time": "True"}.items()
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", os.path.join(
                get_package_share_directory("amiibot_description"),
                "rviz",
                "display.rviz"
            )
        ],
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    depth_to_scan = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        parameters=[{
            'target_frame': 'depth_camera',
            'transform_tolerance': 0.01,
            'min_height': -0.50,
            'max_height': 0.5,
            'angle_min': -0.7854,   # -45 deg
            'angle_max': 0.7854,    # +45 deg
            'angle_increment': 0.00872,  # 0.5 deg
            'scan_time': 1.0 / 15.0,
            'range_min': 0.3,
            'range_max': 10.0,
            'use_inf': True,
        }],
        remappings=[
            ('cloud_in', '/depth_camera/points'),
            ('scan', '/scan_depth'),
        ]
    )

    return LaunchDescription([
        world_name_arg,
        gazebo,
        controller,
        joystick,
        rviz,
        TimerAction(period=6.0, actions=[ekf]),
        TimerAction(period=6.0, actions=[depth_to_scan]),
    ])
