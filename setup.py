from setuptools import setup

setup(
    name='fix_docs',
    version='0.1',
    py_modules=[],
    packages=['hooks'],
    entry_points={
        'console_scripts': [
            'fix_docs = hooks.fix_docs:main',
        ],
    },
)