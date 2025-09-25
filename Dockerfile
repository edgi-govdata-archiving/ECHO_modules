# This docker image uses the official Docker image of [OSS] Apache Spark v3.5.0 as the base container
# Note: Python version in this image is 3.9.2 and is available as `python3`.
# Note: PySpark v3.5.0 (https://spark.apache.org/docs/latest/api/python/getting_started/install.html#dependencies)
ARG BASE_CONTAINER=spark:3.5.1-scala2.12-java17-python3-ubuntu
FROM node:23.11.0-slim as node_base

FROM $BASE_CONTAINER as spark
FROM spark as delta

# Docker image was created and tested with the versions of following packages.
USER root
ARG DELTA_SPARK_VERSION="3.1.0"
ARG DELTALAKE_VERSION="0.16.4"
ARG JUPYTERLAB_VERSION="4.0.7"
ARG PANDAS_VERSION="2.2.2"

# We are explicitly pinning the versions of various libraries which this Docker image runs on.
RUN pip install --quiet --no-cache-dir delta-spark==${DELTA_SPARK_VERSION} \
deltalake==${DELTALAKE_VERSION} jupyterlab==${JUPYTERLAB_VERSION} pandas==${PANDAS_VERSION} python-dotenv

# Install all other dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --quiet --no-cache-dir -r /tmp/requirements.txt

COPY --from=node_base /usr/local/bin /usr/local/bin
COPY --from=node_base /usr/local/lib /usr/local/lib

# Verify installation
RUN node -v && npm -v

# Environment variables
FROM delta as startup
ARG WORKDIR=/opt/spark/work-dir
ENV DELTA_PACKAGE_VERSION=delta-spark_2.12:${DELTA_SPARK_VERSION}

# OS Installations Configurations
RUN apt -qq update
RUN apt -qq -y install vim curl tree
RUN mkdir -p /opt/spark/work-dir/epa-data

# COPY ALL THE FILES
COPY . /opt/spark/work-dir

# Rebuilds the Jupyter Lab configuration
CMD ["bash", "-c", "jupyter lab clean && jupyter lab run"]

# Establish entrypoint
ENTRYPOINT ["bash", "startup.sh"]
