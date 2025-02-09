from setuptools import setup, find_packages

setup(
    name='cha_authentication',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=5.1',
        'djangorestframework>=3.12',
    ],
    entry_points={
        'console_scripts': [
            'authentication=authentication.__main__:main',
        ],
    },
    author='Wassim Chaguetmi',
    author_email='wassim.chaguetmi@gmail.com',
    description='A Django app for multi-token authentication, and some other stuff.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/authentication',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.12',
    ],
)