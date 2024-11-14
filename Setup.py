# setup.py
from setuptools import setup

setup(
    name='rsa-signer',
    version='1.0.0',
    author='RPS',
    packages=['rsa_signer'],
    install_requires=[
        'pycryptodome>=3.18.0',
        'rich>=13.4.2',
        'pyperclip>=1.8.2',
        'appdirs>=1.4.4',
    ],
    entry_points={
        'console_scripts': [
            'sc2signer=rsa_signer.main:main',
        ],
    },
    url='https://github.com/R-P-S/SC2-RSA',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)