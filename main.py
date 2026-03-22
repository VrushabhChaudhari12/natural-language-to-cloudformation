"""
Main entry point for the Natural Language to CloudFormation Generator.
Runs all four scenarios and generates CloudFormation templates.
"""

import os
import sys

# Add the current directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mock_requests import get_request, get_context
from generator import generate_template
from output_writer import save_template


# List of scenarios to run
SCENARIOS = ["ecs_fargate_alb", "eks_nodegroup", "s3_static_site", "rds_postgres"]


def main():
    """
    Run all four scenarios and generate CloudFormation templates.
    """
    print("\n" + "=" * 70)
    print("NATURAL LANGUAGE TO CLOUDFORMATION GENERATOR")
    print("=" * 70 + "\n")

    for scenario in SCENARIOS:
        print(f"\n{'='*70}")
        print(f"SCENARIO: {scenario}")
        print(f"{'='*70}\n")

        # Get the plain-English request
        request_text = get_request(scenario)
        print(f"Infrastructure Request:\n{request_text}\n")

        # Get the context
        context = get_context(scenario)
        print(f"Infrastructure Context: {context}\n")

        print("-" * 70)
        print("Generating CloudFormation template...")
        print("-" * 70)

        try:
            # Generate the template
            yaml_content = generate_template(request_text, context)

            # Save the template
            save_template(yaml_content, scenario)

            # Print first 50 lines of generated YAML to console
            print("\nGenerated YAML (first 50 lines):")
            print("-" * 70)
            yaml_lines = yaml_content.split('\n')
            for line in yaml_lines[:50]:
                print(line)
            if len(yaml_lines) > 50:
                print(f"... ({len(yaml_lines) - 50} more lines)")
            print("-" * 70)

        except Exception as e:
            print(f"\nERROR: Failed to generate template for {scenario}")
            print(f"Error details: {e}\n")
            continue

        # Print separator between scenarios
        print("\n" + "=" * 70)
        print("SCENARIO COMPLETED")
        print("=" * 70 + "\n")

    print("\n" + "=" * 70)
    print("ALL SCENARIOS COMPLETED")
    print("=" * 70)
    print(f"\nGenerated CloudFormation templates:")
    for scenario in SCENARIOS:
        filepath = os.path.join(os.getcwd(), f"template_{scenario}.yml")
        print(f"  - {filepath}")
    print()


if __name__ == "__main__":
    main()