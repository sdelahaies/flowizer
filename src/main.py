"""_summary_ 

_description_

:param _param_: _description_

Main function to run the workflow from a yaml file or a json file. The function will generate the json workflow from the yaml file if needed, then run the workflow and return the final dto.
The final dto will be printed and saved in a file with the same name as the input file but with the extension _output.json


:return: _description_
:rtype: _type_
"""

from workflow import Workflow
from dotenv import load_dotenv
from yaml2json_workflow import generate_json_workflow
from pprint import pprint
import json
import sys
from datetime import datetime

load_dotenv("../.env") 

# write the script below if __main__ block as a function
def run_workflow(dto_path=None, dto=None, verbose=True):
    """Execute a workflow from a JSON or YAML configuration file.

    This function orchestrates workflow initialization and execution by creating a Workflow instance, processing input nodes, and managing the entire workflow lifecycle. It supports loading workflow configurations from either a file path or a pre-loaded dictionary.

    Args:
        dto_path (str, optional): Path to a workflow configuration file (JSON or YAML).
        dto (dict, optional): Pre-loaded workflow configuration dictionary.
        verbose (bool, optional): Enable detailed logging and output. Defaults to True.

    Returns:
        dict: The final workflow data transfer object with updated node statuses and outputs.

    Raises:
        Exception: If neither dto_path nor dto is provided.
        FileNotFoundError: If the specified configuration file cannot be found.
        json.JSONDecodeError: If the JSON file is malformed.
        yaml.YAMLError: If the YAML file cannot be parsed.
    """
    #dto=None
    if dto is None:
        if dto_path is None:
            raise Exception("You need to provide a dto_path or a dto")
            #return
        if dto_path.endswith('.yaml'):
            dto=generate_json_workflow(dto_path, verbose=verbose)
        else:
            with open(dto_path) as f:
                dto = json.load(f)

    
    workflow = Workflow(dto,verbose=verbose)

    # initialize the workflow
    input_nodes = workflow.init_workflow()
    # Start the workflow
    workflow.process_workflow(input_nodes)

    #for node in workflow.nodes:
    #    print(f"{node} count: {workflow.nodes[node].count}")

    # if verbose:
    #     print()
    #     print("\033[5;38;5;162m------------ FINAL DTO ------------\033[0;0m")
    #     pprint(workflow.dto, width=300, depth=4)
    dto_out=workflow.dto
    del workflow.nodes
    del workflow
    return dto_out


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        exit("You need at least 2 argument: python main.py <path-to-dto> <verbose>")

    dto_path=sys.argv[1]
    if len(sys.argv) > 2:
        verbose = sys.argv[2]
    dto=run_workflow(dto_path,verbose=verbose)

    #print(json.dumps(dto, indent=4))
    print("\033[5;38;5;162m------------ FINAL DTO ------------\033[0;0m")
    pprint(dto, width=300, depth=4)

    # save the final dto
    with open(f"{dto_path.replace('.yaml','_output.json')}", 'w') as f:
        json.dump(dto, f, indent=4)
    