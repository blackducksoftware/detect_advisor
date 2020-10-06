import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="synopsys-detect-advisor",
    version="0.95-beta",
    author="Matthew Brady",
    author_email="w3matt@gmail.com",
    description="Assist users when scanning projects using the Synopsys Detect program to scan projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matthewb66/detect_advisor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
