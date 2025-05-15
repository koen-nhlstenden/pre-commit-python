from setuptools import setup

setup(
    name='fix_docs',
    version='0.1',
    py_modules=['hooks.fix_docs'],
    entry_points={
        'console_scripts': [
            'fix-docs = hooks.fix_docs:main',  # adjust to actual function
        ],
    },
)