from setuptools import find_packages, setup

setup(
    name='humidifier',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'pandas',
        'numpy',
        'matplotlib',
        'mpld3'
    ],
)