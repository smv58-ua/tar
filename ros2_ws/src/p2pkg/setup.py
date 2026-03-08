import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'p2pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
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
            'server = p2pkg.nodopub_ejercicio2:main',
            'client = p2pkg.nodosub_ejercicio2:main'
        ],
    },
)
