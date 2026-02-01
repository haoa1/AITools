from setuptools import setup, find_packages
import os

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get version from environment or default
version = os.environ.get("AITOOLS_VERSION", "1.0.0")

# Define dependencies
install_requires = [
    "requests>=2.28.0",
    "beautifulsoup4>=4.11.0",
    "lxml>=4.9.0",
    "pdfplumber>=0.9.0",
    "pypdf>=3.0.0",
    "reportlab>=4.0.0",
    "pdf2image>=1.16.0",
    "python-dotenv>=1.0.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0",
    "sqlite-utils>=3.30.0",
    "pyyaml>=6.0",
]

# Optional dependencies
extras_require = {
    "ai": [
        "openai>=1.0.0",
        "tiktoken>=0.5.0",
    ],
    "web": [
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
    ],
    "pdf": [],  # PDF dependencies are already included in required dependencies
    "data": [
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
    ],
    "database": [
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "mysql-connector-python>=8.0.0",
    ],
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
    ],
    "all": [
        "openai>=1.0.0",
        "tiktoken>=0.5.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "mysql-connector-python>=8.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
    ]
}

setup(
    name="aitools-framework",
    version=version,
    author="AITools Development Team",
    author_email="aitools@example.com",
    description="A modular AI tools framework for command-line interfaces and tool integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haoa1/AITools",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    py_modules=['main'],
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "aitools=main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/haoa1/AITools/issues",
        "Source": "https://github.com/haoa1/AITools",
        "Documentation": "https://github.com/haoa1/AITools/wiki",
    },
    keywords="ai tools framework cli automation",
)