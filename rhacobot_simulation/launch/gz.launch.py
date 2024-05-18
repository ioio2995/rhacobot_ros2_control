from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare 
from launch.event_handlers import OnProcessExit

import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("rhacobot_description"), "urdf", "rhacobot.urdf.xacro"]
            ),
            " ",
            "use_simulation:=true",
            " ",
            "controllers:=true",
        ]
    )
    robot_description = {"robot_description": robot_description_content}
    pkg_share = get_package_share_directory("rhacobot_simulation")
    
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    pkg_share_control = get_package_share_directory('rhacobot_control')

    controllers = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share_control, 'launch/controllers.launch.py'))
    )

    pkg_share_description = get_package_share_directory('rhacobot_description')

    visualization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            pkg_share_description, 'launch/visualization.launch.py'))
    )

    # Gz launch
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': ' -r ' + pkg_share + '/worlds/home.world'
        }.items(),
    )

    gz_sim_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-string', robot_description_content,
                   '-name', 'robot',
                   '-allow_renaming', 'true',
                   '-z', '0.4'],
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
                   '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
                   '/gps/fix@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat',
                   ],
        output='screen'
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description]
    )

    robot_steering_node = Node (
        package="rqt_robot_steering",
        executable="rqt_robot_steering",
        parameters=[{"default_topic": "/wheel_controller/cmd_vel_unstamped"}] 
    )

    return LaunchDescription([
        robot_state_publisher_node,
        visualization,
        gz_sim,
        gz_sim_spawn_entity,
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=gz_sim_spawn_entity,
                on_exit=[controllers],
            )
        ),
        bridge,
        robot_steering_node,
    ])