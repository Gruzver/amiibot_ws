import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    nav_dir = get_package_share_directory('amiibot_navigation')
    desc_dir = get_package_share_directory('amiibot_description')

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz2'
    )

    use_slam_arg = DeclareLaunchArgument(
        'use_slam',
        default_value='false',
        description='Run slam_toolbox for mapping (true) or Nav2 with pre-built map (false)'
    )

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(nav_dir, 'maps', 'isaac_map.yaml'),
        description='Map yaml for Nav2 (only used when use_slam:=false)'
    )

    ekf = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            os.path.join(nav_dir, 'config', 'ekf_isaac.yaml'),
            {'use_sim_time': True}
        ]
    )

    # Joints fijos del URDF (Isaac Sim Transform Tree solo publica joints de física)
    tf_laser = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0.16', '--y', '0', '--z', '0.325',
                   '--yaw', '3.14159265', '--pitch', '0', '--roll', '0',
                   '--frame-id', 'base_link', '--child-frame-id', 'laser'],
        parameters=[{'use_sim_time': True}]
    )

    tf_imu = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0', '--y', '0', '--z', '0.10',
                   '--yaw', '0', '--pitch', '0', '--roll', '0',
                   '--frame-id', 'base_link', '--child-frame-id', 'imu'],
        parameters=[{'use_sim_time': True}]
    )

    tf_depth_camera = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0.14', '--y', '0', '--z', '0.6',
                   '--yaw', '0', '--pitch', '0', '--roll', '0',
                   '--frame-id', 'base_link', '--child-frame-id', 'depth_camera'],
        parameters=[{'use_sim_time': True}]
    )

    tf_depth_optical = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0', '--y', '0', '--z', '0',
                   '--yaw', '-1.5708', '--pitch', '0', '--roll', '-1.5708',
                   '--frame-id', 'depth_camera', '--child-frame-id', 'depth_camera_optical_frame'],
        parameters=[{'use_sim_time': True}]
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(desc_dir, 'rviz', 'isaac_sim.rviz')],
        output='screen',
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('use_rviz'))
    )

    # --- Próximos pasos (descomentar cuando estén listos en Isaac Sim) ---

    depth_to_scan = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        parameters=[{
            'target_frame': 'depth_camera',
            'min_height': -0.50,
            'max_height': 0.5,
            'angle_min': -0.7854,
            'angle_max': 0.7854,
            'angle_increment': 0.00872,
            'scan_time': 1.0 / 15.0,
            'range_min': 0.3,
            'range_max': 10.0,
            'use_inf': True,
            'use_sim_time': True,
            'qos_overrides./depth_camera/points.subscription.reliability': 'best_effort',
        }],
        remappings=[
            ('cloud_in', '/depth_camera/points'),
            ('scan', '/scan_depth'),
        ]
    )

    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            os.path.join(nav_dir, 'config', 'slam_params_isaac.yaml'),
            {'use_sim_time': True}
        ],
        condition=IfCondition(LaunchConfiguration('use_slam'))
    )

    nav2 = IncludeLaunchDescription(
        os.path.join(nav_dir, 'launch', 'nav2_bringup.launch.py'),
        launch_arguments={
            'use_sim_time': 'True',
            'map': LaunchConfiguration('map'),
            'params_file': os.path.join(nav_dir, 'config', 'nav2_params_isaac.yaml'),
        }.items(),
        condition=UnlessCondition(LaunchConfiguration('use_slam'))
    )

    return LaunchDescription([
        use_rviz_arg,
        use_slam_arg,
        map_arg,
        ekf,
        tf_laser,
        tf_imu,
        tf_depth_camera,
        tf_depth_optical,
        rviz,
        TimerAction(period=3.0, actions=[depth_to_scan]),
        TimerAction(period=5.0, actions=[slam]),
        TimerAction(period=5.0, actions=[nav2]),
    ])
