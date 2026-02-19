from setuptools import setup, find_packages

setup(
    name="smart-wms",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.28.1",
        "pandas==2.0.3",
        "plotly==5.17.0",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "numpy==1.24.3",
        "pillow==10.0.0",
        "protobuf==3.20.3",
    ],
)
