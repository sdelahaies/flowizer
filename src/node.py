from nodes.nodes import *
import emoji
from pubsub import pub

class Node:
    """A class representing a workflow node with execution and tracking capabilities.

    The Node class manages the state, execution, and inter-node communication within a workflow system. It handles node initialization, status tracking, and message-based node progression.

    Attributes:
        name (str): The unique identifier of the node.
        type (str): The type of node determining its execution function.
        upstream (list): List of upstream node names.
        downstream (list): List of downstream node names.
        data (dict): Node-specific input, parameters, and output data.
        status (str): Current execution status of the node.
        completed_upstreams (set): Set of upstream nodes that have completed execution.
        workflow (object): Reference to the parent workflow object.
        mode (str, optional): Execution mode, defaults to 'standard'.
        branch (str, optional): Branch identifier, defaults to 'main'.
    """  
    def __init__(self, node_data,workflow):
        """Initialize a Node instance with workflow and node-specific configuration.

        Args:
            node_data (dict): Dictionary containing node configuration details.
            workflow (object): Parent workflow object managing the node.
        """        
        self.name = node_data['name']
        self.type = node_data['type']
        self.upstream = node_data['upstream']
        self.downstream = node_data['downstream']
        self.data = node_data['data']
        self.status = node_data['status']
        self.completed_upstreams = set()
        self.workflow = workflow
        self.mode = 'standard'
        if 'param' in list(node_data['data'].keys()) and node_data['data']['param'] is not None:
            if 'mode' in list(node_data['data']['param'].keys()):
                self.mode = node_data['data']['param']['mode']
            else:
                self.mode = 'standard' 
        else:
            self.mode = 'standard'
        self.branch = 'main'
        if 'param' in list(node_data['data'].keys()) and node_data['data']['param'] is not None:
            if 'branch' in list(node_data['data']['param'].keys()):
                self.branch = node_data['data']['param']['branch']
            else:
                self.branch = 'main' 
        else:
            self.branch = 'main'
        self.count=0
        #print(f"Node {self.name} created")
        #print(f"Node {self.name} mode: {self.mode}")
        pub.subscribe(self.listener, self.name)

    def listener(self, arg):
        """Listens for and processes messages targeting this node.

        Args:
            arg (dict): Message containing action instructions for the node.
        """
        if self.status in ['completed', 'pass']:
            return

        # Check if all upstream nodes are completed
        for upstream_node in self.upstream:
            if upstream_node not in self.completed_upstreams:
                return

        #if arg is not None:
        if 'action' in list(arg.keys()):
            if arg['action'] == 'go':
                self.run_node()
            if arg['action'] == 'pass':
                self.pass_node()


    def run_node(self):
        """Executes the node's specific task and manages workflow progression.

        Runs the node's type-specific function, updates node status, and triggers downstream node execution.
        """
        function = globals()[self.type]
        input = self.data['input']
        param = self.data['param']
        output = function(input,param=param)
        self.status = 'completed'
        #self.count+=1
        if 'error' in list(output.keys()):
            emo=node_state = emoji.emojize(':orange_circle:')
        else:
            emo=node_state = emoji.emojize(':green_circle:')
            
        if self.workflow.verbose:
            # print()
            print(f" \033[96m->\033[0;0m Node \033[1;38;5;208m{self.name:15}\033[0;0m task \033[1;38;5;77m{self.status:12}\033[0;0m", emo)
        self.workflow.update_node_in_dto(self.name, self.status)

        # hydrate node data with function output
        for node in self.workflow.dto['workflow']:
            if node['name'] == self.name:
                node['data']['output'] = output
            
        # Mark this node as completed upstream for downstream nodes
        for downstream_node in self.downstream:
            if downstream_node in self.workflow.nodes:
                self.workflow.nodes[downstream_node].mark_upstream_completed(self.name)

        for downstream_node in self.downstream:
            # hydrate downstream nodes data with function output
            for node in self.workflow.dto['workflow']:                  
                if node['name'] == downstream_node:
                    node['data']['input'][self.name] = self.data['output']
                            
        # Notify downstream nodes ###  wait until previous loop is done otherwise I may send the message before it is hydrated(?) not sure why this would happen
        for downstream_node in self.downstream:
            if self.mode == 'conditional':
                if downstream_node == output['branch']:
                    pub.sendMessage(downstream_node, arg={"action":"go"})
                else:
                    pub.sendMessage(downstream_node, arg={"action":"pass"})
            else:
                pub.sendMessage(downstream_node, arg={"action":"go"})
            
    def pass_node(self):
        """Marks the node as passed and manages workflow progression for conditional flows.

        Updates node status and triggers appropriate downstream node actions based on workflow configuration.
        """
        output={'action':'pass'}
        self.workflow.update_node_in_dto(self.name, 'pass')
        self.status = 'pass'
        self.count+=1
        if 'error' in list(output.keys()):
            emo=node_state = emoji.emojize(':orange_circle:')
        elif 'action' in list(output.keys()) and output['action']=='pass':
            emo=node_state = emoji.emojize(':white_circle:')
        else:        
            emo=node_state = emoji.emojize(':green_circle:')            
        if self.workflow.verbose:
            print(f" \033[96m--\033[0;0m Node \033[1;38;5;208m{self.name:15}\033[0;0m task \033[1;38;5;77m{self.status:12}\033[0;0m", emo)
        self.workflow.update_node_in_dto(self.name, self.status)
        
            # Mark this node as completed upstream for downstream nodes
        for downstream_node in self.downstream:
            if downstream_node in self.workflow.nodes:
                self.workflow.nodes[downstream_node].mark_upstream_completed(self.name)

        for downstream_node in self.downstream:
            if self.workflow.nodes[downstream_node].branch == self.branch:
                pub.sendMessage(downstream_node, arg={"action":"pass"})
            else:
                pub.sendMessage(downstream_node, arg={"action":"go"})

    def mark_upstream_completed(self, upstream_node):
        """Tracks the completion status of upstream nodes.

        Args:
            upstream_node (str): Name of the upstream node that has completed execution.
        """
        self.completed_upstreams.add(upstream_node)