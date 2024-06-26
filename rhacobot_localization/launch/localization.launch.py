# /bin/python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    pkg_rhacobot_localization = get_package_share_directory("rhacobot_localization")

    map_transform_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="map_transform",
        output="screen",
        arguments="--x -1 --y 0 --z 0 --roll 0 --pitch 0 --yaw 0 --frame-id map --child-frame-id odom".split(
            " "
        ),
    )

    navsat_transform_node = Node(
        package="robot_localization",
        executable="navsat_transform_node",
        name="navsat_transform_node",
        output="screen",
        parameters=[
            {
                "magnetic_declination_radians": 0.0,
                "yaw_offset": 0.0,
                "zero_altitude": True,
                "use_odometry_yaw": False,
                "wait_for_datum": False,
                "publish_filtered_gps": False,
                "broadcast_utm_transform": False,
                "use_simtime": True,
            }
        ],
        remappings=[
            ("/odometry/filtered", "/odom"),
        ],
    )

    body_localization_node = Node(
        package="robot_localization",
        executable="ekf_node",
        name="body_ekf_node",
        output="screen",
        respawn=True,
        parameters=[os.path.join(pkg_rhacobot_localization, "config/ukf.yaml")],  
        )
    
    tail_arm_ekf_node = Node(
        package="robot_localization",
        executable="ekf_node",
        name="tail_arm_ekf_node",
        output="screen",
        respawn=True,
        parameters=[os.path.join(pkg_rhacobot_localization, "config/ukf.yaml")],  
        )
    
    base_localization_node = Node(
        package="robot_localization",
        executable="ekf_node",
        name="base_ekf_node",
        output="screen",
        respawn=True,
        parameters=[os.path.join(pkg_rhacobot_localization, "config/ukf.yaml")],
        remappings=[
            ("/odometry/filtered", "/odom"),
        ],     
    )

    return LaunchDescription(
        [
            base_localization_node,
            body_localization_node,
            #tail_arm_ekf_node,
            #navsat_transform_node,
            map_transform_node,
        ]
    )

