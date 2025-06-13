# ECHO Modules Delta

ECHO_modules_delta is a modified version of the ECHO_modules, updated to work with [the ECHO-Pipeline project](https://github.com/edgi-govdata-archiving/ECHO-Pipeline) which harnesses the Delta Lake system using PySpark. 

## Background
TBD

## How to Use
### Using the ECHO tables in a local Delta Lake system
This mode is for when you have Delta Lake set up on your local machine and want to use it without relying on API services.

1. Copy the example environment file:
    ```bash
    cp .env.example .env
    ```

2. Set up your `.env` file by updating the required paths. Refer to the environment variables section below.

3. Build the Docker container:
   ```bash
   docker compose build
   ```
4. Start the container:
    ```bash
    docker compose up
    ```

This will start the services defined in the **echo-delta-compose.yaml** file which is the ECHO Modules app and any dependencies (e.g., Spark, Delta Lake, etc.). A bash script `startup.sh` runs on start of container which sets up the Spark Session for use. A Jupyter Notebook server will also be launched, allowing you to run notebooks that utilize the ECHO_modules.

5. (Optional) To enter the container's shell:
    ```bash
    docker exec -it echo-modules bash
    ```
6. Environment Variables

    Add the following variables to a `.env` file for the application to run:

    Variable | Description | Example
    ---------|-------------|--------
    | `DELTA_TABLES_HOST_PATH` | (Optional) Path to the Delta tables on your host machine. Only required if **not** using the API. | `/home/user/epa-data/delta-tables`    |
    | `SCHEMA_HOST_PATH`       | (Optional) Path to the schema directory on your host. Only required if **not** using the API.       | `/home/user/epa-data/schema`          |
    | `WORK_DIR_HOST_PATH`     | Path to your working directory on the host machine. Used for accessing notebooks locally within the container. | `/home/user/ECHO_Modules_delta`       |

**Notes:**
- `DELTA_TABLES_HOST_PATH` and `SCHEMA_HOST_PATH` are unnecessary if you're using the API to access data.
- `WORK_DIR_HOST_PATH` is used to mount your local working directory (e.g., for Jupyter notebooks) into the container environment for development.
- Ensure that all specified paths in your `.env` file exist and are correctly mounted in your Docker setup.

### Using the ECHO tables in the ECHO API server
If you do not use a local Delta Lake docker container, you can still access the ECHO tables from the ECHO API server using ECHO_modules_delta.


1. Create a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. Install the required packages in `requirements.txt`: 
    ```bash
    pip install -r requirements.txt
    ```
    Ensure Jupyter Lab is installed in the virtual environment so you can access the notebook interface.

3. Start Jupyter Lab:
    ```bash
    jupyter lab
    ```

4. Generate an access token:

    Use the `get_echo_api_access_token` function to generate an access token from the ECHO API server to authenticate your requests.

    - Follow the API server's authentication instructions to obtain your token.

5. Set the access token in your notebook when prompted. You should now be able to use the API server to request data. 

## License & Copyright
Copyright (C) Environmental Data and Governance Initiative (EDGI) This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.0.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the [LICENSE](LICENSE) file for details.
