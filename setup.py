from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="task-manager-simulator",
    version="0.1.0",
    author="PyTaskManager Team",
    author_email="",
    description="Simulador del Administrador de Tareas de Windows en Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yofreca/PyTaskManager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "task-manager=task_manager_simulator.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "task_manager_simulator": [
            "resources/icons/*",
            "resources/styles/*",
            "resources/images/*",
        ],
    },
)
