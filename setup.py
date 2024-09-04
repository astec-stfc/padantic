from setuptools import setup, find_packages
import versioneer

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["pydantic>=2", "pyyaml>=6", "numpy>=1.26"]

setup(
    name="PAdantic",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="James Jones",
    author_email="james.jones@stfc.ac.uk",
    description="A pydantic model for particle accelerators",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://gitlab.stfc.ac.uk/jkj62/padantic",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    package_data={"PAdantic": ["PV_Values.yaml"]},
)
