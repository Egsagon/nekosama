from setuptools import setup

classifiers = [ # idk what is this lets just assume its true
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

if __name__ == "__main__":
    setup(
    name='nekosama',
    version='3.0.1',
    description='An API for the neko-sama website.',
    long_description=open('README.md').read(),
    url='https://github.com/Egsagon/neko-sama-api',
    author='Egsagon',
    author_email='egsagon12@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='nekosama',
    packages=find_packages(),
    install_requires=['']
)
