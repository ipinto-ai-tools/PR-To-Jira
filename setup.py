from setuptools import find_packages, setup

setup(
    name="pr-jira-tool",
    version="1.0.0",
    description="CLI tool for syncing GitHub PRs with Jira tickets",
    author="Your Name",
    author_email="your-email@example.com",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        "PyGithub>=2.1.1",
        "jira>=3.5.0",
        "click>=8.1.7",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "pr-jira-tool=pr_jira_tool.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
)
