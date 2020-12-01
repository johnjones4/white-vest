import setuptools
from glob import glob

with open("Readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="whitevest-johnjones4",
    version="0.0.1",
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
    data_files=[
        ("dashboard", glob("dashboard/build/*/**"))
    ],
    classifiers=[],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "whitevest-ground=whitevest.bin.ground:main",
            "whitevest-air=whitevest.bin.air:main"
        ]
    }
)
