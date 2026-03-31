from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="True",
    )

    joint_state_broadcaster_spawner = TimerAction(
        period=5.0,  # espera a que Gazebo/ros2_control cargue
        actions=[Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        )]
    )

    wheel_controller_spawner = TimerAction(
        period=6.0,  # 1s después del broadcaster
        actions=[Node(
            package="controller_manager",
            executable="spawner",
            arguments=["amiibot_controller", "--controller-manager", "/controller_manager"],
        )]
    )

    return LaunchDescription([
        use_sim_time_arg,
        joint_state_broadcaster_spawner,
        wheel_controller_spawner,
    ])