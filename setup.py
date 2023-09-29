from setuptools import setup, find_packages

setup(
    name="ttpbuilder",
    version="0.1.0",
    description="A GUI Front end for creating TTP Templates",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Scott Peterman",
    author_email="scottpeterman@gmail.com",
    url="https://github.com/scottpeterman/ttpbuilder",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        'PyQt6==6.5.1',
        'PyQt6-WebEngine==6.5.0',
        'ttp==0.9.5',

    ],

    entry_points={
        'console_scripts': [
            'ttpbuilder=ttpbuilder.ttpgui:main',
        ],
    },
    python_requires='>=3.9',
)
