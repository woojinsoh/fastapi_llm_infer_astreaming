## FastAPI LLM Inference Async Stream Implentation

The contents in this repository is for demonstrating the LLM inference with asynchronous stream using the APIs from OPENAI, NVIDIA NIM, or NAVER HYPERCLOVA on FastAPI. 

## Prerequisite
1. Prepare for the keys for the LLM platforms(NGC, OPENAI, Clova Studio)
    - [NGC](https://docs.nvidia.com/ai-enterprise/deployment/spark-rapids-accelerator/latest/appendix-ngc.html)
    - [OPENAI](https://platform.openai.com/api-keys)
    - [ClovaStudio](https://api.ncloud-docs.com/docs/clovastudio-completions)

2. Assign the keys within `key_config.env` file.
    ```bash
    $ source key_config.env
    ```
    - Then check if those keys are propely assigned as environment variables by executing `env` command.
    ```bash
    $ env 
    SHELL=/bin/bash
    NGC_CLI_API_KEY=xxxxx
    ...
    NVIDIA_API_KEY=nvapi-....
    ...
       
    ```

3. Deploy NVIDA NIM on your server for the self-Hosted API.
    - Local deployment of NIM service requires the NVAIE license.
    - For example, how to deploy NIM for [mistralai/mistral-7b-instruct-v0.3](https://build.nvidia.com/mistralai/mistral-7b-instruct-v03?snippet_tab=Docker) on your host is described in NGC.


4. Install the python dependencies.
    ```bash
    $ pip3 install -r requirements.txt
    ```

## Quick start
1. Launch the FastAPI server.
    ```
    python3 launch.py
    ```

2. Inference.
    - The inference works as an asynchronous stream. 
    ```
    python3 client.py -p "nim" -q "who is the president of Korea?"
    ```
    - Sample output is
    ```
    [PLATFORM]: NIM
    [QUERY]: who is the president of Korea?
    [STATUS CODE]: 200
    [STREAMING RESPONSES]
    {"status": "processing", "data": " Moon"}
    {"status": "processing", "data": " J"}
    {"status": "processing", "data": "ae"}
    {"status": "processing", "data": "-"}
    {"status": "processing", "data": "in"}
    {"status": "processing", "data": " is"}
    {"status": "processing", "data": " the"}
    {"status": "processing", "data": " current"}
    {"status": "processing", "data": " president"}
    {"status": "processing", "data": " of"}
    {"status": "processing", "data": " South"}
    {"status": "processing", "data": " Korea"}
    {"status": "processing", "data": "."}
    {"status": "complete", "data": "Stream finished"}

    [FULL RESPONSE]
    Moon Jae-in is the current president of South Korea.
    ```