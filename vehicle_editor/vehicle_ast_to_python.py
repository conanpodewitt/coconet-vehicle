#!/usr/bin/env python3

import json
import sys
import argparse
from typing import List, Dict, Any, Optional


def extract_networks_from_ast(ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
	"""
	Extract network information from an AST JSON representation.
	
	The AST follows a specific pattern where networks are defined as function parameters:
	
	Main
	└── DefFunction
		├── Provenance
		├── FunctionName
		├── Type (Pi type)
		└── Lam (lambda definition)
			└── Binder
				├── Provenance
				├── NetworkName
				└── NetworkType
	
	Args:
		ast_data: The AST data as a dictionary
		
	Returns:
		A list of dictionaries containing information about each network found in the AST
	"""
	networks = []
	
	# Early return if not a Main node
	if ast_data.get("tag") != "Main":
		return networks
	
	# Process each function definition
	for item in ast_data.get("contents", []):
		if item.get("tag") != "DefFunction":
			continue

		network_info = extract_network_from_function(item)

		if network_info:
			networks.append(network_info)
	
	return networks


def extract_network_from_function(function_node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
	"""Extract network information from a function definition node."""
	function_contents = function_node.get("contents", [])

	if len(function_contents) < 4:
		return None
	
	# Define the network
	network_info = {}
	
	# Extract function node
	function_name = function_contents[1]
	network_info["function_name"] = function_name
	
	# Extract lambda node
	lambda_node_index = 3
	if lambda_node_index >= len(function_contents):
		return None
	lambda_node = function_contents[lambda_node_index]
	
	extract_network_from_lambda(lambda_node, network_info)
	return network_info


def extract_network_from_lambda(lambda_node: Dict[str, Any], network_info: Dict[str, Any]):
	"""Extract network information from a lambda definition node."""
	if lambda_node.get("tag") != "Lam":
		return None
	
	lambda_contents = lambda_node.get("contents", [])
	if len(lambda_contents) < 1:
		return None
	
	# Extract binder node
	binder_node = lambda_contents[0]

	extract_network_from_binder(binder_node, network_info)


def extract_network_from_binder(binder_node: Dict[str, Any], network_info: Dict[str, Any]):
	"""Extract network information from a binder node."""
	if binder_node.get("tag") != "Binder":
		return None
	
	binder_contents = binder_node.get("contents", [])
	if len(binder_contents) < 3:
		return None
	
	# Extract network name and signature
	network_name = binder_contents[1]
	network_info["name"] = network_name
	contents = binder_contents[2]["contents"]
	network_info["signature"] = {"input": contents[0], "output": contents[1]}


def main():
	parser = argparse.ArgumentParser(description='Extract network definitions from Vehicle AST JSON')
	parser.add_argument('ast_file', help='Path to the AST JSON file')
	parser.add_argument('--format', choices=['json', 'minimal'], default='minimal',
					  help='Output format (json, or minimal)')
	parser.add_argument('--names-only', action='store_true', help='Only output network names')
	args = parser.parse_args()
	
	try:
		with open(args.ast_file, 'r') as f:
			ast_data = json.load(f)
		
		networks = extract_networks_from_ast(ast_data)
		
		if not networks:
			print("No networks found in the AST.")
			return
		
		# Handle different output formats
		if args.names_only:
			for network in networks:
				print(network['name'])
				
		elif args.format == 'json':
			print(json.dumps(networks, indent=2))

		elif args.format == 'minimal':
			for network in networks:
				name = network['name']
				defined_in = network['function_name']
				print(f"{name} (defined in {defined_in})")
	
	except FileNotFoundError:
		print(f"Error: File '{args.ast_file}' not found.")
		sys.exit(1)
	except json.JSONDecodeError:
		print(f"Error: File '{args.ast_file}' is not a valid JSON file.")
		sys.exit(1)

if __name__ == "__main__":
	main() 