from setuptools import setup, find_packages

setup(
    name="smart-wms",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.22.0",
        "pandas==1.5.3",
        "numpy==1.23.5",
        "plotly==5.14.0",
        "requests==2.28.2",
    ],
)
