from setuptools import setup, find_packages

setup(
    name='myextension',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'jupyterlab',
    ],
    entry_points={
        'jupyter_serverproxy_servers': [
            'myextension = myextension:setup_handlers',
        ]
    },
)
