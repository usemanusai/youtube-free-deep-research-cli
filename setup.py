"""
Setup script for YouTube Chat CLI.
"""

from setuptools import setup, find_packages
import pathlib

# Read README for long description
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="youtube-chat-cli",
    version="2.1.0",
    description="AI-powered CLI tool for YouTube video analysis, channel monitoring, and automated content processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/usemanusai/youtube-free-deep-research-cli",
    author="YouTube Chat CLI Team",
    author_email="use.manus.ai@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Communications :: Chat",
        "Topic :: System :: Monitoring",
    ],
    keywords="cli, ai, youtube, channel-monitoring, tts, transcription, n8n, rag, automation",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8, <4",

    # Dependencies
    install_requires=requirements,

    # Development dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "tts": [
            "gtts>=2.3.0",
            "edge-tts>=6.1.0",
            "torch>=2.0.0",
            "torchaudio>=2.0.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-mock>=3.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "gtts>=2.3.0",
            "edge-tts>=6.1.0",
            "torch>=2.0.0",
            "torchaudio>=2.0.0",
        ],
    },

    # Project structure
    package_data={
        "youtube_chat_cli": ["*.template"],
    },

    # Include all data files
    include_package_data=True,

    # Entry points for console scripts
    entry_points={
        "console_scripts": [
            "youtube-chat=youtube_chat_cli.cli.main:main",
            "youtube-chat-cli=youtube_chat_cli.cli.main:main",
        ],
    },

    project_urls={
        "Bug Reports": "https://github.com/usemanusai/youtube-free-deep-research-cli/issues",
        "Source": "https://github.com/usemanusai/youtube-free-deep-research-cli",
        "Documentation": "https://github.com/usemanusai/youtube-free-deep-research-cli#readme",
    },

    # Additional metadata
    license="MIT",
    platforms=["any"],
    zip_safe=False,
)
