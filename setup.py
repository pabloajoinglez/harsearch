from setuptools import setup, find_packages

setup(
    name='harsearch',
    version='0.1.0',
    description='A command line tool for searching through HAR files',
    author='Pablo Ajo',
    packages=find_packages(),
    install_requires=[
        'colorama>=0.4.0',
    ],
    entry_points={
        'console_scripts': [
            'harsearch = harsearch.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

