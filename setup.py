from setuptools import setup, find_packages

setup(
    name="synapticbricks",
    version="1.4.1",  # Added AIHealer - autonomous LLM-powered healing
    description="Autonomous Living Code Ecosystem: Self-Healing Bricks, Predictive Failure (Phantom), AI Immune System (Aegis), LLM Auto-Repair (AIHealer), and Real-Time Dashboard (Pulse)",
    author="Medo & Neura",
    packages=find_packages(),
    package_data={
        "synapticbricks": ["pulse/*.py"],
    },
    install_requires=[
        "psutil",
        "flask>=2.0",
        "requests>=2.25",  # For AIHealer Gemini API calls
    ],
    extras_require={
        "pulse": ["flask>=2.0"],
        "ai": ["requests>=2.25"],  # Optional: for AIHealer
    },
    entry_points={
        "console_scripts": [
            "synaptic-pulse=synapticbricks.pulse.server:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
)
