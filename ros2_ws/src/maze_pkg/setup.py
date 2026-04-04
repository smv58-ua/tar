import os
from glob import glob
from setuptools import setup

package_name = 'maze_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Instalar la carpeta launch
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # Instalar la carpeta worlds
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='smv2458', 
    maintainer_email='tu_correo@email.com', # Cambia esto si quieres
    description='Paquete para resolver el laberinto con Turtlebot3',
    license='Apache-2.0', # O la licencia que uses
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'maze_solver_node = maze_pkg.maze_solver:main',
            'maze_solver_pledge_node = maze_pkg.maze_solver_pledge:main'
        ],
    },
)