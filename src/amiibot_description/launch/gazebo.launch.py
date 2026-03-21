from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, IncludeLaunchDescription, TimerAction
from pathlib import Path
import os
from os import pathsep
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    amiibot_description_dir = get_package_share_directory('amiibot_description')

    model_arg = DeclareLaunchArgument(
        name = 'model',
        default_value= os.path.join(amiibot_description_dir, 'urdf', 'amiibot.urdf.xacro'),
        description='Path to the URDF model file'
    )

    world_name_arg = DeclareLaunchArgument(
        name='world_name',
        default_value = "empty"
    )

    world_path = PathJoinSubstitution([
        amiibot_description_dir,
        'worlds',
        PythonExpression(expression=["'",LaunchConfiguration('world_name'),"'","+'.world'"])
    ])

    model_path = str(Path(amiibot_description_dir).parent.resolve())
    model_path += pathsep + os.path.join(amiibot_description_dir, 'models')

    gazebo_resource_path = SetEnvironmentVariable(
        "GZ_SIM_RESOURCE_PATH", 
        model_path
    )

    ros_distro = os.environ["ROS_DISTRO"]

    amiibot_description = ParameterValue(Command([
        'xacro ',
        LaunchConfiguration('model'),
        " is_simulation:=true",
        ]),
        value_type=str
    )


    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{"robot_description": amiibot_description,
                     "use_sim_time": True}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory("ros_gz_sim"), "launch"), "/gz_sim.launch.py"]),
        launch_arguments= {
                "gz_args": PythonExpression(["'", world_path," -v 4 -r'"])
            }.items(),
        )
    
    gz_spawm_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description',
                   "-name", "amiibot"]
        
    )

    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan"
        ],
        remappings=[
            ('/imu', '/data'),
        ]
    )

    return LaunchDescription([
        model_arg,
        world_name_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        gazebo,
        TimerAction(period=3.0, actions=[gz_spawm_entity]),
        gz_ros2_bridge
    ])
