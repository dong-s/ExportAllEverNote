# coding=utf8

from setuptools import setup, find_packages
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='evernote-export',
    version='1.0.1',
    description='批量导出Evernote中的所有笔记，按照笔记目录，存档到本地对应文件夹',
    long_description=open(os.path.join(here, 'README.md'), encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/dong-s/ExportAllEverNote',
    author='Dong',
    author_email='dong@dong-s.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='evernote export enex',
    packages=find_packages(),
    install_requires=['evernote'],
    extras_require={},
    entry_points={
        'console_scripts': [
            'evernote-export = exportevernote.EverNote:main'
        ]
    },
)
