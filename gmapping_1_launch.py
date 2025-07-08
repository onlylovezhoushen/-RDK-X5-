#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction, DeclareLaunchArgument, ExecuteProcess, LogInfo
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition

def generate_launch_description():
    pkg_dir = get_package_share_directory('rplidar_ros')
    rviz_config = os.path.join(pkg_dir, 'rviz', 'sllidar_gmapping_ros2.rviz')

    scan_topic = LaunchConfiguration('scan_topic', default='scan')
    odom_topic = LaunchConfiguration('odom_topic', default='odom')  
    start_rviz = LaunchConfiguration('start_rviz', default='true')

    return LaunchDescription([
        DeclareLaunchArgument(
            'scan_topic',
            default_value='scan',
            description='Laser scan topic name'
        ),
        DeclareLaunchArgument(
            'odom_topic',  
            default_value='odom',
            description='Odometry topic name'
        ),
        DeclareLaunchArgument(
            'start_rviz',
            default_value='true',
            description='Start RViz if true'
        ),
      
  Node(
            package='rplidar_ros',
            executable='rplidar_node',
            name='rplidar_node',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                'serial_baudrate': 460080,
                'frame_id': 'laser',
                'inverted': False,
                'angle_compensate': True,
                'scan_mode': 'Standard',
                'auto_standby': False
            }],
            remappings=[('scan', scan_topic)],
            output='screen'
        ),
  
  Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_laser',
            arguments=['0.1', '0', '0.2', '0', '0', '0', 'base_link', 'laser'],
            output='screen'
        ),
 TimerAction(
            period=3.0,
            actions=[
                Node(
                    package='slam_gmapping',
                    executable='slam_gmapping',
                    name='slam_gmapping',
                    output='screen',
                    parameters=[{
                        'use_sim_time': False,
                        'map_update_interval': 2.0,
                        'maxUrange': 15.0,
                        'delta': 0.05,
                        'particles': 30,
                        'xmin': -10.0,
                        'ymin': -10.0,
                        'xmax': 10.0,
                        'ymax': 10.0,
                        'linearUpdate': 1.0,
                        'angularUpdate': 0.5,
                    }],
                    remappings=[
                        ('scan', scan_topic),
                        ('odom', odom_topic)  
                    ]
                )
            ]
        ),

        # RViz 鍙鍖栵紙鍙€夊惎鍔級
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': False}],
            condition=IfCondition(start_rviz),
            output='screen'
        ),

        TimerAction(
            period=5.0,
            actions=[
                LogInfo(msg='检查tf树结构'),
                ExecuteProcess(
                    cmd=['ros2', 'run', 'tf2_tools', 'view_frames'],
                    output='screen'
                )
            ]
        )
    ])
