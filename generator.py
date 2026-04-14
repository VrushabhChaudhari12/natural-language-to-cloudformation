"""
Main generator logic for CloudFormation template generation.
Uses OpenAI-compatible client (Ollama by default).
"""
import logging
import time
import yaml
from openai import OpenAI

import config
from prompts import SYSTEM_PROMPT, build_prompt

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


# Custom YAML loader to handle CloudFormation intrinsic functions (!Ref, !Sub, etc.)
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


def select_constructor(loader, node):
    """Construct !Select."""
    return loader.construct_scalar(node)


def join_constructor(loader, node):
    """Construct !Join."""
    return loader.construct_scalar(node)


def split_constructor(loader, node):
    """Construct !Split."""
    return loader.construct_scalar(node)


# Register intrinsic function constructors
for tag, constructor in [
    ("!Ref", ref_constructor),
    ("!Sub", sub_constructor),
    ("!GetAtt", getatt_constructor),
    ("!Equals", equals_constructor),
    ("!If", if_constructor),
    ("!Select", select_constructor),
    ("!Join", join_constructor),
    ("!Split", split_constructor),
]:
    CloudFormationLoader.add_constructor(tag, constructor)


def generate_cloudformation(request_text: str, context: dict) -> str:
    """
    Generate a CloudFormation YAML template from a plain-English request.

    Args:
        request_text: Plain-English infrastructure description
        context: Dictionary with project context

    Returns:
        CloudFormation YAML content as a string
    """
    user_message = build_prompt(request_text, context)

    client = OpenAI(
        base_url=config.BASE_URL,
        api_key=config.API_KEY,
        timeout=config.TIMEOUT_SECONDS,
    )

    previous_outputs: list[str] = []
    retry_count = 0

    while retry_count < config.MAX_RETRIES:
        try:
            log.info("Calling LLM (attempt %d/%d)", retry_count + 1, config.MAX_RETRIES)
            response = client.chat.completions.create(
                model=config.MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
            )

            content = response.choices[0].message.content.strip()

            # Strip markdown fences if present
            if content.startswith("```yaml"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Validate: must contain required CFN keys
            if not all(k in content for k in config.CFN_REQUIRED_KEYS):
                log.warning(
                    "Output missing required CFN keys %s. Retrying...",
                    config.CFN_REQUIRED_KEYS,
                )
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            # Validate YAML is parseable
            try:
                yaml.load(content, Loader=CloudFormationLoader)
                log.info("CFN YAML validation passed")
            except yaml.YAMLError as exc:
                log.warning("YAML validation failed: %s. Retrying...", exc)
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            # Loop detection
            if content in previous_outputs:
                log.warning("Loop detected: identical output. Retrying...")
                previous_outputs.clear()
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            previous_outputs.append(content)
            if len(previous_outputs) >= config.LOOP_DETECTION_THRESHOLD:
                log.warning("Loop detection threshold reached. Using last output.")
                return content

            log.info("CloudFormation template generated successfully")
            return content

        except Exception as exc:
            log.error("Error during generation: %s", exc)
            retry_count += 1
            if retry_count >= config.MAX_RETRIES:
                raise RuntimeError(
                    f"Failed after {config.MAX_RETRIES} retries: {exc}"
                ) from exc
            wait_time = 2 ** retry_count
            log.info("Retrying in %d seconds...", wait_time)
            time.sleep(wait_time)

    raise RuntimeError(
        f"Failed to generate valid CloudFormation template after {config.MAX_RETRIES} retries"
    )


def validate_cloudformation(yaml_content: str) -> bool:
    """
    Validate that the generated YAML is a valid CloudFormation template.

    Args:
        yaml_content: The YAML content to validate

    Returns:
        True if valid CloudFormation structure, False otherwise
    """
    try:
        parsed = yaml.load(yaml_content, Loader=CloudFormationLoader)
        if parsed and isinstance(parsed, dict):
            return all(k in parsed for k in config.CFN_REQUIRED_KEYS)
    except yaml.YAMLError:
        pass
    return False
