from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

# Dependencies
required = ['requests==2.14.2', 'gitpython']

setup(
    name='SimpleSensor',
    version='0.1.0',
    description='A Python IoT framework for simple sensor integration',
    long_description=readme,
    author='',
    author_email='',
    packages=[  'simplesensor', 
                'simplesensor.shared', 
                'simplesensor.cli', 
                'simplesensor.collection_modules', 
                'simplesensor.collection_modules.demographic_camera',
                'simplesensor.communication_modules', 
                'simplesensor.communication_modules.websocket_server',
                'simplesensor.communication_modules.mqtt_client'
                ],
    package_data= {
                    'simplesensor': ['config/*.conf', '../logs/*'],
                    'simplesensor.collection_modules.demographic_camera': ['config/*.conf', 'classifiers/haarcascades/*.xml'],
                    'simplesensor.communication_modules.websocket_server': ['config/*.conf'],
                    'simplesensor.communication_modules.mqtt_client': ['config/*.conf']
                    },
    install_requires=required,
    entry_points = {
        'console_scripts': ['scly=simplesensor.cli.main:main']
    }
)