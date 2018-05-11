from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

# Dependencies
required = ['requests==2.14.2']

setup(
    name='SimpleSensor',
    version='0.1.0',
    description='An IoT Python framework for simple sensor integration',
    long_description=readme,
    author='',
    author_email='',
    packages=[  'simplesensor', 
                'simplesensor.shared', 
                'simplesensor.cli', 
                'simplesensor.collection_modules', 
                'simplesensor.collection_modules.camCollectionPoint',
                'simplesensor.collection_modules.btleCollectionPoint',
                'simplesensor.communication_modules', 
                'simplesensor.communication_modules.websocketServer'
                ],
    package_data= {
                    'simplesensor': ['config/*.conf'],
                    'simplesensor.collection_modules.camCollectionPoint': ['config/*.conf', 'classifiers/haarcascades/*.xml'],
                    'simplesensor.communication_modules.websocketServer': ['config/*.conf']
                    },
    install_requires=required,
    entry_points = {
        'console_scripts': ['scly=simplesensor.cli.main:main']
    }
)