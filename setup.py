from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="testability-analyzer",
    version="1.1.0",
    author="Testability Analyzer Team",
    author_email="team@testability-analyzer.com",
    description="A static analysis tool that evaluates Python code testability and provides refactoring guidance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BenBos71/Testability_Refactoring_Analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pytest>=7.0.0,<9.0.0",
        "black>=22.0.0,<25.0.0",
        "click>=8.0.0,<9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "testability-analyzer=testability_analyzer.cli:main",
        ],
    },
)
