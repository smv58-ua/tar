from setuptools import find_packages, setup

package_name = 'mi_accion'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='smv2458-docker',
    maintainer_email='smv2458-docker@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'server = mi_accion.fibonacci_action_server:main',
            'client = mi_accion.fibonacci_action_client:main',
            'server_ejercicio = mi_accion.ejercicios_fibServer:main',
            'client_ejercicio = mi_accion.ejercicios_fibClient:main',
        ],
    },
)
