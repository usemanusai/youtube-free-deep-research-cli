"""
Setup script for Personal Research Insight CLI.
"""

from setuptools import setup, find_packages
import pathlib

# Read README for long description
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="personal-research-insight-cli",
    version="1.0.0",
    description="AI-powered CLI tool for extracting, processing, and querying content from YouTube videos and websites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/personal-research-insight-cli",  # Update with actual repo URL
    author="Research Insight Team",
    author_email="research-insight@example.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",  # Update if different license
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    keywords="cli, ai, research, youtube, web-scraping, nlp, text-to-speech",
    package_dir={"": "."},
    packages=find_packages(where="."),
    python_requires=">=3.10, <4",

    # Dependencies from requirements.txt
    install_requires=[
        "click>=8.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.25.0",
        "halo>=0.0.31",
        "youtube-transcript-api>=1.2.0",
        "beautifulsoup4>=4.9.0",
        "deepmultilingualpunctuation>=1.0.1",
        "langchain-huggingface>=0.3.0",
        "langchain-openai>=0.1.0",
    ],

    # Development dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.0.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-mock>=3.0.0",
        ],
    },

    # Project structure
    package_data={
        "": [".env.template"],
    },

    # Include all test files
    include_package_data=True,

    # Entry points for console scripts
    entry_points={
        "console_scripts": [
            "research-cli=youtube_chat_cli_main.__main__:main",
            "personal-research-cli=youtube_chat_cli_main.__main__:main",
        ],
    },

    project_urls={
        "Bug Reports": "https://github.com/username/personal-research-insight-cli/issues",
        "Source": "https://github.com/username/personal-research-insight-cli",
        "Documentation": "https://github.com/username/personal-research-insight-cli#readme",
    },

    # Additional metadata
    license="MIT",  # Update as appropriate
    platforms=["any"],
    zip_safe=False,
)
