#from node import Node
from node import Node
from pubsub import pub
from datetime import datetime


class Workflow:
    """A workflow management system that orchestrates node execution and tracking.

    The Workflow class provides a comprehensive framework for creating, initializing, and processing complex computational workflows. It manages node creation, status tracking, and inter-node communication.

    Attributes:
        dto (dict): Workflow data transfer object containing workflow configuration.
        nodes (dict): Dictionary of Node objects mapped by their names.
        verbose (bool): Flag to enable detailed logging and output.
    """
    def __init__(self, dto:dict, verbose:bool=True):
        """Initialize a Workflow instance with workflow configuration.

        Args:
            dto (dict): Workflow data transfer object containing node configurations.
            verbose (bool, optional): Enable verbose logging. Defaults to True.
        """
        self.dto = dto
        self.nodes = self.create_nodes(dto['workflow'])
        self.verbose = verbose

    def create_nodes(self, workflow:list) -> dict:
        """Create Node instances for each node in the workflow configuration.

        Transforms workflow configuration into a dictionary of Node objects, enabling individual node management and execution.

        Args:
            workflow (list): List of node configuration dictionaries.

        Returns:
            dict: A mapping of node names to Node objects.
        """
        nodes = {}
        for node_data in workflow:
            node = Node(node_data, self)
            nodes[node.name] = node
        return nodes

    def process_workflow(self, input_nodes:list[str]):
        """Initiate workflow execution by sending start messages to input nodes.

        Triggers the workflow by sending 'go' actions to specified input nodes, which then propagate through the workflow.

        Args:
            input_nodes (list): Names of nodes to start workflow execution.
        """
        for node_name in input_nodes:
            pub.sendMessage(node_name, arg={"action":"go"})
        

    def update_node_in_dto(self, node_name:str, status:str):
        """Update the status of a specific node in the workflow data transfer object.

        Modifies the node's status and records the completion timestamp in the workflow configuration.

        Args:
            node_name (str): Name of the node to update.
            status (str): New status to assign to the node.
        """
        for node in self.dto['workflow']:
            if node['name'] == node_name:
                # if self.verbose:
                #     print(
                #         f"Updating status of node \033[1;38;5;208m{node_name}\033[0;0m to \033[1;38;5;77m{status}\033[0;0m")
                node['status'] = status
                node['completedAt'] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")

    def init_workflow(self):
        """Initialize the workflow by identifying and marking input nodes.

        Prepares the workflow for execution by marking nodes with no upstream dependencies as completed.

        Returns:
            list: Names of input nodes that can start workflow execution.
        """
        # Mark input nodes as completed
        input_nodes = []
        for node in self.dto['workflow']:
            if node['upstream'] == []:
                node['status'] = 'completed'
                node['completedAt'] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
                input_nodes.append(node['name'])
        return input_nodes
