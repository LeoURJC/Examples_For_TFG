from setuptools import find_packages, setup
import os 
from glob import glob 

package_name = 'movement_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*.launch.py'))

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='leo',
    maintainer_email='l.gomezba.2019@alumnos.urjc.es',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        'movement_server = movement_pkg.movement_server:main',
        'movement_client = movement_pkg.movement_client:main'
        ],
    },
)
