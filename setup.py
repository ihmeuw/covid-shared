import os

from setuptools import find_packages, setup

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    src_dir = os.path.join(base_dir, "src")

    about = {}
    with open(os.path.join(src_dir, "covid_shared", "__about__.py")) as f:
        exec(f.read(), about)

    with open(os.path.join(base_dir, "README.rst")) as f:
        long_description = f.read()

    install_requirements = [
        "click",
        "loguru",
        "pandas",
        "pathos",
        "pyyaml",
        "tqdm",
    ]

    test_requirements = [
        "pytest",
        "pytest-mock",
    ]

    doc_requirements = [
        "sphinx",
    ]

    internal_requirements = [
        "jobmon[ihme]==3.0.5",
        "db_queries>=25.2.0,<26",
    ]

    setup(
        name=about["__title__"],
        version=about["__version__"],
        description=about["__summary__"],
        long_description=long_description,
        url=about["__uri__"],
        author=about["__author__"],
        author_email=about["__email__"],
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        include_package_data=True,
        install_requires=install_requirements,
        extras_require={
            "test": test_requirements,
            "internal": internal_requirements,
            "dev": test_requirements + doc_requirements + internal_requirements,
            "docs": doc_requirements,
        },
        zip_safe=False,
    )
