from typing import Tuple, Dict, List

import networkx as nx
import numpy as np


def human_format(num):
    """
    :param num: A number to print in a nice readable way.
    :return: A string representing this number in a readable way (e.g. 1000 --> 1K).
    """
    magnitude = 0

    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0

    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])  # add more suffices if you need them


def get_new_position_for_node(positions: Dict):
    """
    Get new positions for each one of the nodes.
    :param positions: A dictionary of positions per node.
    :return: A NumPy array containing the new positions.
    """
    positions_array = np.array([x for x in positions.values()])
    new_positions = np.array([positions_array[:, 0].max() + 0.5, positions_array[:, 1].mean()])
    return new_positions


def get_sender_policy_and_id(receiver_node_id, edge_data: Dict) -> Tuple:
    """
    :param receiver_node_id: The receiver node id (i.e. public-key).
    :param edge_data: A dictionary containing the edge's attributes.
    :return: A tuple containing two elements:
                 (1) The policy of the sender (A dictionary containing the fee policy)
                 (2) The id (i.e. public-key) of the sender.
    """
    if receiver_node_id == edge_data['node1_pub']:
        sender_node_i = 2
    elif receiver_node_id == edge_data['node2_pub']:
        sender_node_i = 1
    else:
        raise ValueError(f'The given receiver_node_id {receiver_node_id} is not in the given edge_data {edge_data}.')

    sender_node_policy = edge_data[f'node{sender_node_i}_policy']
    sender_node_id = edge_data[f'node{sender_node_i}_pub']

    return sender_node_policy, sender_node_id


def calculate_route_fees(graph: nx.MultiGraph, route: List, amount: int, get_debug_str: bool = False):
    """
    Calculate the route fees, based on the policies of the nodes on the route.

    :param graph: The graph to work on.
    :param route: The route which is a list of edges.
    :param amount: The amount of money to transfer in the route.
    :param get_debug_str: It true, return a string which is used for debugging purposes.
    :return: The fees for each node in the route.
    """
    total_amount = amount
    fees = list()
    debug_str = " "

    for edge_key in route[::-1]:
        sender_policy, _ = get_sender_policy_and_id(edge_key[1], graph.edges[edge_key])
        fee = int(sender_policy['fee_base_msat'] + (total_amount * sender_policy['fee_rate_milli_msat']))
        if get_debug_str:
            debug_str = f"({human_format(sender_policy['fee_base_msat'])} + " \
                            f"{human_format(total_amount)}*{sender_policy['fee_rate_milli_msat']})={fee} + " + \
                        debug_str
        fees.append(fee)
        total_amount += fee

    if get_debug_str:
        return fees[::-1], debug_str

    return fees[::-1]
