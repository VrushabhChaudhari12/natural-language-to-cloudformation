"""
Main generator logic for CloudFormation template generation.
Uses OpenAI library pointing to Ollama at http://localhost:11434/v1
"""

import time
import yaml
from openai import OpenAI


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


# Configuration constants
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"
OLLAMA_MODEL = "llama3.2"

# Termination safety layers
TERMINATION_CONDITION = "AWSTemplateFormatVersion"
MAX_RETRIES = 3
TIMEOUT_SECONDS = 120
LOOP_DETECTION_THRESHOLD = 3


def generate_template(request_text: str, context: dict) -> str:
    """
    Generate a CloudFormation YAML template from a plain-English request using Ollama.

    Args:
        request_text: The plain-English request description
        context: Dictionary with infrastructure context

    Returns:
        The generated CloudFormation YAML content as a string
    """
    from prompts import SYSTEM_PROMPT, build_prompt

    # Build the user message
    user_message = build_prompt(request_text, context)

    # Initialize the OpenAI client pointing to Ollama
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY,
        timeout=TIMEOUT_SECONDS
    )

    # Track outputs for loop detection
    previous_outputs = []
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            # Make ONE LLM call
            response = client.chat.completions.create(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=8192
            )

            # Extract the generated content
            generated_content = response.choices[0].message.content

            # Clean up the response - remove markdown code blocks if present
            generated_content = generated_content.strip()
            if generated_content.startswith("```yaml"):
                generated_content = generated_content[7:]
            elif generated_content.startswith("```"):
                generated_content = generated_content[3:]
            if generated_content.endswith("```"):
                generated_content = generated_content[:-3]

            generated_content = generated_content.strip()

            # Layer 1: Check termination condition
            if not generated_content.startswith(TERMINATION_CONDITION):
                print(f"Warning: Output does not start with '{TERMINATION_CONDITION}'. Retrying...")
                retry_count += 1
                time.sleep(2 ** retry_count)  # Exponential backoff
                continue

            # Validate YAML is parseable using our custom loader
            try:
                parsed = yaml.load(generated_content, Loader=CloudFormationLoader)
                if not parsed or 'Resources' not in parsed:
                    print("Warning: YAML missing Resources section. Retrying...")
                    retry_count += 1
                    time.sleep(2 ** retry_count)
                    continue
                print("YAML validation passed!")
            except yaml.YAMLError as e:
                print(f"YAML validation failed: {e}. Retrying...")
                retry_count += 1
                time.sleep(2 ** retry_count)  # Exponential backoff
                continue

            # Layer 4: Loop detection
            if generated_content in previous_outputs:
                print("Loop detected: same output repeated. Retrying with different approach...")
                previous_outputs.clear()
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            previous_outputs.append(generated_content)

            # If we have 3 repeated outputs, break the loop
            if len(previous_outputs) >= LOOP_DETECTION_THRESHOLD:
                print("Loop detection threshold reached. Using last output.")
                break

            # Success - return the generated template
            return generated_content

        except Exception as e:
            print(f"Error during generation: {e}")
            retry_count += 1
            if retry_count >= MAX_RETRIES:
                raise Exception(f"Failed after {MAX_RETRIES} retries: {e}")
            # Exponential backoff
            wait_time = 2 ** retry_count
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    # If we exhaust retries, raise an exception
    raise Exception(f"Failed to generate valid CloudFormation template after {MAX_RETRIES} retries")


def validate_template(yaml_content: str) -> bool:
    """
    Validate that the generated YAML is parseable and contains Resources section.

    Args:
        yaml_content: The YAML content to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = yaml.load(yaml_content, Loader=CloudFormationLoader)
        if parsed and isinstance(parsed, dict):
            return 'Resources' in parsed and 'AWSTemplateFormatVersion' in parsed
    except yaml.YAMLError:
        pass
    return False