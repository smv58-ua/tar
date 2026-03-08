#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():

    arg_numero = DeclareLaunchArgument(
        'numero',
        default_value='7',
        description='Valor de entrada para el nodo publicador'
    )

    numero_config = LaunchConfiguration('numero')

    return LaunchDescription([
        arg_numero,
        Node(
            package='p2pkg',
            executable='server',
            name='nodopub_ejercicio2',
            parameters=[{'numero': numero_config}],
            namespace='miGrupo',
            remappings=[('/topic_ejercicio2', '/miGrupo/topic_ejercicio2')]
        ),
        Node(
            package='p2pkg',
            executable='client',
            name='nodosub_ejercicio2',
            namespace='miGrupo',
            remappings=[('/topic_ejercicio2', '/miGrupo/topic_ejercicio2')]
        )
    ])