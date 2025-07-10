from setuptools import setup, find_packages
import versioneer

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["pydantic>=2", "pyyaml>=6", "numpy>=1.26"]

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    package_data={
        "PAdantic": [
            "Machines/**/*.yaml",
            "PV_Values.yaml",
        ]
    },
)
