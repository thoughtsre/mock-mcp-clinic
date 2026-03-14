> **This repo has been migrated to [GitHub](https://github.com/thoughtsre/mock-mcp-clinic).**

# Clinic MCP Server (HTTP)

A simple Model Context Protocol (MCP) server for a mock doctor's clinic, served over HTTP and deployable to AWS ECS.

## Features

- List available doctors and specialties
- Get clinic contact information
- Make an appointment given a condition (simple specialty matching)

## Local Development

### Requirements

- Python 3.11+
- pip

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

Server listens on `http://0.0.0.0:8000` by default. Configure with env vars:

- `HOST` (default `0.0.0.0`)
- `PORT` (default `8000`)

### MCP HTTP Endpoints

This server uses MCP over HTTP (SSE). If your client supports MCP HTTP transport, point it to the base URL.

### Tools

- `list_doctors()` → returns list of doctors with specialties
- `clinic_contact()` → returns clinic contact info
- `make_appointment(condition, preferred_time?, requestor_name?, requestor_phone?)` → returns confirmation

## Docker

```bash
docker build -t clinic-mcp:latest .
docker run --rm -p 8000:8000 clinic-mcp:latest
```

## AWS ECS (Fargate)

1. Create an ECR repo and push the image:

```bash
aws ecr get-login-password --region ap-southeast-1 \
  | docker login --username AWS --password-stdin {{accountID}}.dkr.ecr.ap-southeast-1.amazonaws.com
docker tag clinic-mcp:latest {{accountID}}.dkr.ecr.ap-southeast-1.amazonaws.com/clinic-mcp:latest
docker push {{accountID}}.dkr.ecr.ap-southeast-1.amazonaws.com/clinic-mcp:latest
```

2. Register task definition using `ecs-task-definition.json` (edit ARNs, region, image):

```bash
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json
```

3. Create ECS service (Fargate) in your cluster with an ALB or public IP, allowing inbound TCP 8000.

4. Verify logs in CloudWatch Logs group `/ecs/clinic-mcp`.

## AWS CDK (Fargate + ALB)

An AWS CDK app is provided under `cdk/` to deploy an internet-facing ALB Fargate service that builds the container image from this repo.

```bash
cd cdk
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cdk bootstrap   # once per account/region
cdk deploy
```

Note: The CDK stack outputs the ALB DNS name. Traffic on port 80 is forwarded to the container on port 8000.

## Testing

```bash
pytest -q
```

## Helper script

Run locally with a script that honors `HOST` and `PORT` env vars:

```bash
./run_local.sh
```


## Notes

- This is a demo; `make_appointment` returns a mock confirmation without persistence.
- Adjust doctor list and specialty mapping in `server.py` as desired.


