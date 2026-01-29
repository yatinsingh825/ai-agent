from setuptools import setup, find_packages

setup(
    name="ai-call-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dotenv',
    ],
)
