"""
Output writer for saving generated CloudFormation templates.
"""

import os
import yaml


# Custom YAML loader to handle CloudFormation intrinsic functions
class CloudFormationLoader(yaml.SafeLoader):
    """Custom YAML loader for CloudFormation templates with !Ref, !Sub, etc."""
    pass


def ref_constructor(loader, node):
    """Construct !Ref as a simple string."""
    return loader.construct_scalar(node)


def sub_constructor(loader, node):
    """Construct !Sub as a simple string."""
    return loader.construct_scalar(node)


def getatt_constructor(loader, node):
    """Construct !GetAtt as a simple string."""
    return loader.construct_scalar(node)


def equals_constructor(loader, node):
    """Construct !Equals."""
    return loader.construct_scalar(node)


def if_constructor(loader, node):
    """Construct !If."""
    return loader.construct_scalar(node)


# Register constructors for CloudFormation tags
CloudFormationLoader.add_constructor('!Ref', ref_constructor)
CloudFormationLoader.add_constructor('!Sub', sub_constructor)
CloudFormationLoader.add_constructor('!GetAtt', getatt_constructor)
CloudFormationLoader.add_constructor('!Equals', equals_constructor)
CloudFormationLoader.add_constructor('!If', if_constructor)
CloudFormationLoader.add_constructor('!Join', sub_constructor)
CloudFormationLoader.add_constructor('!FindInMap', sub_constructor)


def save_template(yaml_content: str, scenario_name: str) -> None:
    """
    Save the generated CloudFormation template to a file and print a formatted summary.

    Args:
        yaml_content: The generated CloudFormation YAML content
        scenario_name: The name of the scenario (e.g., 'ecs_fargate_alb', 'eks_nodegroup')
    """
    # Save to template_{scenario_name}.yml in current directory
    filename = f"template_{scenario_name}.yml"
    filepath = os.path.join(os.getcwd(), filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    # Parse the YAML to extract info for summary using custom loader
    try:
        parsed = yaml.load(yaml_content, Loader=CloudFormationLoader)
    except yaml.YAMLError:
        # Fallback to safe_load if custom loader fails
        parsed = yaml.safe_load(yaml_content)

    # Count resources generated
    resources_count = 0
    resource_types = []
    if parsed and 'Resources' in parsed:
        resources_count = len(parsed['Resources'])
        resource_types = list(parsed['Resources'].keys())

    # Print formatted summary
    print("=" * 60)
    print("CLOUDFORMATION TEMPLATE SAVED SUCCESSFULLY")
    print("=" * 60)
    print(f"Scenario Name:      {scenario_name}")
    print(f"Resources Generated: {resources_count}")
    print(f"Resource Types:     {', '.join(resource_types[:5])}")
    if len(resource_types) > 5:
        print(f"                     ... and {len(resource_types) - 5} more")
    print(f"File Location:      {filepath}")
    print("=" * 60)