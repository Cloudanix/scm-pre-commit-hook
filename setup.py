from setuptools import find_packages
from setuptools import setup


with open("requirements.txt", 'r') as f:
    requirements = f.read()

setup(
    name="cloudanix-scanner",
    description="Pre-commit hook that scans for secrets and vulnerabilities.",
    url="",
    py_modules=["main"],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires=">=3.8",
    platforms=["Linux"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        "console_scripts": [
            "cloudanix=main:main",
        ],
    },
)