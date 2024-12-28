#!../venv/bin/ python

import os
import secrets
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from werkzeug.utils import secure_filename
from yaml2json_workflow import generate_json_workflow
from main import run_workflow
import json
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import yaml
from draw_dag import draw_dag

app = FastAPI(
    title="Flowiser Workflow Engine",
    description="A simple workflow engine for running DAG workflows",
)

inputname = None
app.secret_key = secrets.token_urlsafe(16)

# uncomment to run the app
# comment to run build the doc
UPLOAD_FOLDER = "../uploads"
CONFIG_FOLDER = "../config"
OUTPUT_FOLDER = "../outputs"
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")


@app.post("/runflow")
async def run_flow(config: str = None) -> dict:
    """Execute a workflow using a specified configuration.

    This asynchronous endpoint triggers workflow execution using a specified configuration file and returns the results of the workflow processing.

    Args:
        config (str, optional): The name of the configuration file to use. Defaults to None.

    Returns:
        dict: The output data from the final node of the workflow.

    Raises:
        HTTPException: If no configuration file is provided (status code 400) or if no output node is found in the workflow (status code 500).
    """
    global inputname
    if config is None:
        raise HTTPException(status_code=400, detail="No configuration file provided")

    dto = generate_json_workflow(os.path.join(CONFIG_FOLDER, config))
    for node in dto["workflow"]:
        if node["name"] == "FileInput":
            node["data"]["input"]["filename"] = inputname

    with open(os.path.join(CONFIG_FOLDER, "tmp_config.json"), "w") as f:
        json.dump(dto, f, indent=4)

    print("\033[1;38;5;11m ---------------------- \033[0;0m")
    print("\033[1;38;5;11m ---  RUN WORKFLOW  --- \033[0;0m")
    print("\033[1;38;5;11m ---------------------- \033[0;0m")
    result = run_workflow(dto_path=os.path.join(CONFIG_FOLDER, "tmp_config.json"))
    output = None
    for node in result["workflow"]:
        if node["name"] == "Output":
            output = node["data"]["output"]

    if output is None:
        raise HTTPException(status_code=500, detail="Output node not found in workflow")

    fname = f"{dto['name']}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json"
    with open(os.path.join(OUTPUT_FOLDER, fname), "w") as f:
        json.dump(result, f, indent=4)
    print(f"\033[96m Output saved at {os.path.join(OUTPUT_FOLDER, fname)}\033[0;0m")
    print("\033[1;38;5;11m ---------------------- \033[0;0m")
    print()
    return result


@app.post("/run_from_react")
async def run_from_react():
    """Execute a workflow initiated from a React frontend and return the results.

    This asynchronous endpoint triggers workflow execution using a previously uploaded file configuration and returns the workflow output. It ensures a file has been uploaded before running the workflow.

    Returns:
        JSONResponse: The output data from the final node of the workflow.

    Raises:
        HTTPException: If no file has been uploaded (status code 400) or if no output node is found in the workflow (status code 500).
    """
    global inputname
    if inputname is None:
        raise HTTPException(status_code=400, detail="No file uploaded")


    print("\033[1;38;5;11m ---------------------- \033[0;0m")
    print("\033[1;38;5;11m ---  RUN WORKFLOW  --- \033[0;0m")
    print("\033[1;38;5;11m ---------------------- \033[0;0m")

    result = run_workflow(dto_path=os.path.join(CONFIG_FOLDER, "tmp_config.json"))
    output = None
    for node in result["workflow"]:
        if node["name"] == "Output":
            output = node["data"]["output"]
    print("\033[1;38;5;11m ---------------------- \033[0;0m")
    print()
    if output is None:
        raise HTTPException(status_code=500, detail="Output node not found in workflow")

    return JSONResponse(content=output)


# create a clean endpoint to remove all the uploaded files
@app.delete("/clean")
async def clean_files(folder: str = "outputs"):
    """Remove all files from the upload folder.

    This asynchronous endpoint clears the upload directory by deleting all files, helping to manage temporary file storage and prevent disk space accumulation.

    Returns:
        dict: A status confirmation indicating successful file deletion.

    Raises:
        OSError: If there are permission issues or file deletion fails.
    """
    if folder == "uploads":
        # get all files in the uploads folder
        files = os.listdir(UPLOAD_FOLDER)
        # remove all files
        for file in files:
            os.remove(os.path.join(UPLOAD_FOLDER, file))
        return {"status": "Upload folder cleaned"}

    if folder == "outputs":
        files = os.listdir(OUTPUT_FOLDER)
        # remove all files
        for file in files:
            os.remove(os.path.join(OUTPUT_FOLDER, file))
        return {"status": "Output folder cleaned"}


@app.post("/drawdag")
async def drawdag(config: str = None, CONFIG_FOLDER:str= CONFIG_FOLDER, OUTPUT_FOLDER: str = OUTPUT_FOLDER, outfile:str=None,fmt: str = "png"):
    #try:
    with open(os.path.join(CONFIG_FOLDER,config)) as f:
        data=yaml.load(f, Loader=yaml.FullLoader)
    print(data)
    print(fmt)
    if outfile is None:
        outfile = f"{OUTPUT_FOLDER}/{config.split('.')[0]}.{fmt}"
    draw_dag(data, outfile, fmt,view=False)
    return {"status": f"DAG drawn and saved in {OUTPUT_FOLDER}"}
    #except Exception as e:
    #    return {"error": str(e)}    
    

# create a healthcheck endpoint
@app.get("/healthcheck")
async def healthcheck():
    """Perform a simple health check on the API service.

    This asynchronous endpoint provides a basic status check to confirm that the API is operational and responsive.

    Returns:
        dict: A status confirmation indicating the service is running.
    """
    return {"status": "ok"}


if __name__ == "__main__":

    print("\033[1;38;5;11m   _____           _            \033[0;0m")
    print("\033[1;38;5;11m  / _/ /__ _    __(_)__ ___ ____\033[0;0m")
    print("\033[1;38;5;11m / _/ / _ \ |/|/ / /_ // -_) __/\033[0;0m")
    print("\033[1;38;5;11m/_//_/\___/__,__/_//__/\__/_/   \033[0;0m")
    print()
    print(
        "\033[96mrepository: \033[00m\033[1;38;5;11mhttps://github.com/sdelahaies/flowizer\033[0;0m"
    )
    print()
    print("\033[92mready... \033[0;0m")
    print()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8100,log_config=None)

# uvicorn api:app --host 0.0.0.0 --port 8100 --reload --log-level critical