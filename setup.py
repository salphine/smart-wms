from setuptools import setup, find_packages

setup(
    name="smart-wms",
    version="1.0.0",
    packages=find_packages(exclude=["frontend", "tests"]),
    install_requires=[
        # Backend only - Frontend has separate requirements
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
    ],
)
