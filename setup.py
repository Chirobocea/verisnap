from setuptools import setup, find_packages
import platform

# Determine the platform
current_platform = platform.system()

# Define the common dependencies
install_requires = []

# Add platform-specific dependencies
if current_platform == 'Windows':
    install_requires.extend([
        'winshell>=0.6',
        'pywin32>=306',
    ])

setup(
    name='verisnap',
    version='0.1.0',
    author='Mihail Chirobocea',
    author_email='mihail.chirobocea@s.unibuc.ro',
    description='A tool to create directory snapshots with size-based file copying or symlinking',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Chirobocea/verisnap',
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
