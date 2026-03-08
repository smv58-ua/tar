#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='primer_paquete',
            executable='server',
            name='nodo_envia',
        ),
        Node(
            package='primer_paquete',
            executable='client',
            name='nodo_recibe',
        )
    ])