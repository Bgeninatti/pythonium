import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.build.txt", "r") as rf:
    requirements = list(rf.readlines())

setuptools.setup(
    name="pythonium",
    version="0.3.0b0",
    author="Bruno Geninatti",
    author_email="brunogeninatti@gmail.com",
    description="A space strategy algorithmic-game build in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bgeninatti/pythonium",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    extras_require={
        "render": ["matplotlib==3.4.3"]
    },
    python_requires=">=3.7",
    scripts=["bin/pythonium"],
    include_package_data=True,
    data_files=[('font', ['font/jmh_typewriter.ttf'])],
)
