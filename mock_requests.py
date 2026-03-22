"""
Mock developer requests for CloudFormation template generation.
Each request is a plain-English description of what infrastructure needs to be built.
"""

# Dictionary of scenario requests
REQUESTS = {
    "ecs_fargate_alb": "Create an ECS Fargate service with an Application Load Balancer, 2 tasks running on port 80, CloudWatch logging, and auto-scaling between 2 and 10 tasks",
    "eks_nodegroup": "Create an EKS cluster called prod-cluster with a managed node group of 3 t3.medium instances across 2 availability zones with IAM OIDC provider enabled",
    "s3_static_site": "Create an S3 bucket for static website hosting with CloudFront distribution, HTTPS only, and Origin Access Control",
    "rds_postgres": "Create an RDS PostgreSQL 15 instance, db.t3.micro, Multi-AZ disabled, 20GB storage, in a private subnet, with Secrets Manager for the password"
}

# Context dictionary for each scenario
CONTEXT = {
    "ecs_fargate_alb": {
        "stack_name": "ecs-fargate-alb",
        "region": "us-east-1",
        "account_id": "123456789012",
        "vpc_cidr": "10.0.0.0/16",
        "cluster_name": "my-cluster",
        "service_name": "my-service"
    },
    "eks_nodegroup": {
        "stack_name": "eks-cluster",
        "region": "us-east-1",
        "account_id": "123456789012",
        "cluster_name": "prod-cluster",
        "nodegroup_name": "prod-nodegroup",
        "instance_type": "t3.medium",
        "desired_size": 3,
        "min_size": 2,
        "max_size": 4
    },
    "s3_static_site": {
        "stack_name": "s3-static-site",
        "region": "us-east-1",
        "account_id": "123456789012",
        "bucket_name": "my-static-site-bucket",
        "domain_name": "www.example.com"
    },
    "rds_postgres": {
        "stack_name": "rds-postgres",
        "region": "us-east-1",
        "account_id": "123456789012",
        "db_instance_identifier": "mypostgresdb",
        "db_name": "mydb",
        "db_instance_class": "db.t3.micro",
        "allocated_storage": 20
    }
}


def get_request(scenario: str) -> str:
    """
    Get the plain-English request description for a given scenario.

    Args:
        scenario: The scenario name (e.g., 'ecs_fargate_alb', 'eks_nodegroup')

    Returns:
        The plain-English request description as a string
    """
    return REQUESTS.get(scenario, "")


def get_context(scenario: str) -> dict:
    """
    Get the context dictionary for a given scenario.

    Args:
        scenario: The scenario name

    Returns:
        Dictionary containing project context (stack_name, region, account_id, etc.)
    """
    return CONTEXT.get(scenario, {})