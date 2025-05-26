# tfdslib
Utitlity functions for use n the CLI as well as plugins and notebooks.


# Development
## PySpark
We keep the package form installing pysparkand assume there will be a pyspark wherever it gets installed. This avoids messing with spark versions, which is a pain.
To maintain and test the spark parts of the package you need to install the spark dependencies in the poetry venv:

    poetry run pip install pyspark==3.5.5
    poetry run pip install delta-spark==3.3.0

You can check the Dockerfile for the tfds Spark plugin to see whet version is currently in development:
https://github.com/jens-koster/the-free-data-stack/blob/main/spark/Dockerfile

## linting

    poetry run pre-commit run --files $(find src -type f)

## build
see readme for the devpi plugin for setting up devpi and poetry global configs the first time.

Regular build and publish is then simply:
    poetry build
    poetry publish -r devpi
