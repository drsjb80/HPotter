from setuptools import setup, find_packages

setup(name='hpotter',
    version='1.0',
    author='Steve Beaty',
    author_email='drjsb80@gmail.com',
    url='https://github.com/drsjb80/HPotter',
    packages=find_packages(),
    data_files=[
        ('hpotter',
            ['hpotter/env.py',
            'hpotter/logging.conf',
            'hpotter/requirements.txt',
            'README.md']
        )
    ],
    description='An easy to install, configure, and run honeypot',
    long_description='''An easy to install, configure, and run honeypot.
It is also relatively straightfoward to extend it to new protocols and
specific, fake servers.''',
    install_requires=['SQLAlchemy', 'SQLAlchemy-Utils', 'paramiko'],
    license='Python-2.0',
)
