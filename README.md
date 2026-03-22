# Natural Language to CloudFormation Generator

An AI-powered generator that takes plain-English infrastructure descriptions and produces production-ready AWS CloudFormation YAML templates.

## Overview

This project uses a local LLM (Ollama with llama3.2) to generate AWS CloudFormation templates from simple infrastructure requests. The generated templates include:

- **ECS Fargate**: Service with ALB, auto-scaling, CloudWatch logging
- **EKS Cluster**: Managed node groups with IAM OIDC provider
- **S3 Static Site**: Bucket with CloudFront distribution and HTTPS
- **RDS PostgreSQL**: Instance with Secrets Manager, private subnet

## Stack

- **Language**: Python 3.10+
- **LLM**: Ollama (localhost:11434) with llama3.2 model
- **Dependencies**: openai, pyyaml

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Ensure Ollama is running with the llama3.2 model:

```bash
ollama serve
# In another terminal:
ollama pull llama3.2
```

## Usage

Run the generator for all four scenarios:

```bash
py main.py
```

This will:
1. Process each of the four infrastructure scenarios
2. Generate production-ready CloudFormation YAML templates
3. Save them as `template_{scenario}.yml` in the current directory
4. Print the generated YAML to the console

## Output

The tool generates CloudFormation templates for each scenario:

- `template_ecs_fargate_alb.yml`
- `template_eks_nodegroup.yml`
- `template_s3_static_site.yml`
- `template_rds_postgres.yml`

## Example

Input (Infrastructure Request):
```
"Create an ECS Fargate service with an Application Load Balancer, 2 tasks running on port 80, CloudWatch logging, and auto-scaling between 2 and 10 tasks"
```

Output (Generated CloudFormation):
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'ECS Fargate Service with ALB and Auto Scaling'

Parameters:
  Environment:
    Type: String
    Default: dev
  ProjectName:
    Type: String

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-vpc

  Cluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Ref ProjectName

  ALB:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Scheme: internet-facing
      Type: application

  Service:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref Cluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      LoadBalancers:
        - ContainerName: web
          ContainerPort: 80
          TargetGroupArn: !Ref TargetGroup

Outputs:
  ClusterName:
    Value: !Ref Cluster
    Export:
      Name: !Sub ${AWS::StackName}-ClusterName

  ALBDNSName:
    Value: !GetAtt ALB.DNSName
    Export:
      Name: !Sub ${AWS::StackName}-ALBDNSName
```

## Features

- **Four-Layer Termination Safety**:
  1. Checks output starts with "AWSTemplateFormatVersion"
  2. Maximum 3 retries with exponential backoff
  3. 120-second timeout per request
  4. Loop detection to break on repeated outputs

- **YAML Validation**: All generated templates are validated using Python's yaml.safe_load and checked for Resources section

- **Production-Ready**: Includes proper CloudFormation intrinsic functions (!Ref, !Sub, !GetAtt), Tags, and Outputs

## Supported AWS Services

- ECS Fargate with Application Load Balancer
- EKS Cluster with managed node groups
- S3 Bucket with CloudFront distribution
- RDS PostgreSQL with Secrets Manager
- VPC, Subnets, Security Groups
- IAM Roles and policies
- Application Auto Scaling

## License

MIT