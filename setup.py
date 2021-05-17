import re
import ast

from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('pimotioncam/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

    setup(
        name='piMotionCamera',
        version='0.0.1',
        packages=['pimotioncam'],
        url='https://github.com/jpunkt/piMotionCamera',
        license='LGPL',
        author='jpunkt',
        author_email='johannes@arg-art.org',
        description='Script for an art installation which prints images from picamera and file system',

        install_requires=[
                             'click',
                             # 'opencv-python',
                             'numpy',
                             'picamera'
                         ],

        entry_points='''
                     [console_scripts]
                     pimotion=pimotioncam.cli:pimotion
                     '''
    )
