from distutils.core import setup

setup(name='hpotter',
    version='1.0',
    packages=['framework', 'plugins', 'web'],
    package_dir={
        'framework': 'src/framework',
        'plugins': 'src/plugins',
        'web': 'src/web',
    },
    url='https://github.com/drsjb80/HPotter',
    data_files=[
        ('src',
            ['src/env.py',
            'src/logging.conf',
            'src/requirements.txt',
            'src/README.md']
        )
    ],
    author='Steve Beaty',
    author_email='drjsb80@gmail.com',
)
