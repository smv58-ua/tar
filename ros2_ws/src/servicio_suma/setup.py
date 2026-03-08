from setuptools import find_packages, setup

package_name = 'servicio_suma'

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
    maintainer='tamai-docker',
    maintainer_email='tamai.ramirez.ua@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'server = servicio_suma.add_two_ints_server:main',
            'client = servicio_suma.add_two_ints_client:main'
        ],
    },
)
