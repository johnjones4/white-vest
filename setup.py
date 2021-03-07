import setuptools
import os

with open("Readme.md", "r") as fh:
    long_description = fh.read()

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths

extra_files = package_files("dashboard/build")

setuptools.setup(
    name="whitevest-johnjones4",
    version="0.0.4",
    author="John Jones",
    author_email="john@johnjones.family",
    description="White Vest is a project for collecting, logging, emitting, and visualizing telemetry from a model rocket containing an inboard Raspberry Pi Zero with another Raspberry Pi receiving telemetry.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/johnjones4/white-vest",
    packages=[
        "whitevest",
        "whitevest.bin",
        "whitevest.lib",
        "whitevest.threads"
    ],
    package_data={'': extra_files},
    classifiers=[],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "whitevest-ground=whitevest.bin.ground:main",
            "whitevest-air=whitevest.bin.air:main"
        ]
    }
)
