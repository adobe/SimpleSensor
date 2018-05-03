from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

# Dependencies
required = ['requests']

setup(
    name='SimpleSensor',
    version='0.1.0',
    description='An IoT Python framework for simple sensor integration',
    long_description=readme,
    author='',
    author_email='',
    packages=['src', 'src.main', 'src.cli', 'src.collection_modules', 'src.communication_modules'],
    install_requires=required,
    entry_points = {
        'console_scripts': ['scly=src.cli.main:main']
    }
)