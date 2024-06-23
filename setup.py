from setuptools import setup, find_packages

setup(
    name='iceicedata',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'selenium',
        'paho-mqtt',
        'pytz'
    ],
    entry_points={
        'console_scripts': [
            'iceicedata = iceicedata.main:main'
        ]
    }
)
