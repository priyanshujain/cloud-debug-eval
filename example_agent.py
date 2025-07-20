#!/usr/bin/env python3
"""
Example external agent for testing the evaluation framework.
This is just a demo - real agent would be separate.
"""

class ExampleAgent:
    """Example agent that returns hardcoded solutions for testing."""
    
    def solve_problem(self, problem: str) -> str:
        """
        Solve a debugging problem given the context.
        
        Args:
            problem_context: Full problem context with logs/configs
            
        Returns:
            Solution string
        """
        # For demo purposes, return the exact expected solution
        # Your real agent would analyze the problem_context and generate a solution
        
        if problem == "k8s-github-secret-failure":
            return """# Root Cause Analysis

The GitHub user account `devops-automation` was removed from the GitHub organization during the security team's "cleanup" operation yesterday. This account was the owner of the Personal Access Token (PAT) used in the Kubernetes secret `github-registry-secret` for authenticating with GitHub Container Registry.

# Diagnosis Steps

## 1. Examine Pod Events
```bash
kubectl describe pod -n fintech-prod -l app=payment-processor
```
**Findings**: Pods failing with `ImagePullBackOff` and authentication errors when pulling from `ghcr.io`

## 2. Check Secret Configuration
```bash
kubectl get secret github-registry-secret -n fintech-prod -o yaml
echo "eyJhdXRocyI6eyJnaGNyLmlvIjp7InVzZXJuYW1lIjoiZGV2b3BzLWF1dG9tYXRpb24iLCJwYXNzd29yZCI6ImdocF9SNGw5VDBrZW5fQjNmNGtlX2V4YW1wbGVfdG9rZW4xMjM0NSIsImF1dGgiOiJaR1YyYjNCekxXRjFkRzl0WVhScGIyNDZaMmh3WDFJMGJEbFVNR3RsYmw5Q00yWTBhMlZmWlhoaGJYQnNaVjkwYjJ0bGJqRXlNelExIn19fQ==" | base64 -d
```
**Findings**: Secret contains credentials for user `devops-automation` with PAT starting with `ghp_R4l9T0ken_`

## 3. Test GitHub Authentication
```bash
curl -H "Authorization: token ghp_R4l9T0ken_B3f4ke_example_token12345" https://api.github.com/user
```
**Findings**: Returns `Bad credentials` error, confirming the token/account is invalid

# Solution

## 1. Create New Service Account in GitHub
Create new user: `k8s-registry-service` and add to organization with appropriate permissions.

## 2. Generate New Personal Access Token
Generate new PAT with scopes: read:packages, repo

## 3. Update Kubernetes Secret
```bash
kubectl create secret docker-registry github-registry-secret-new \
  --docker-server=ghcr.io \
  --docker-username=k8s-registry-service \
  --docker-password=ghp_NEW_TOKEN_HERE \
  --docker-email=devops@fintech-company.com \
  -n fintech-prod --dry-run=client -o yaml > new-secret.yaml

kubectl delete secret github-registry-secret -n fintech-prod
kubectl apply -f new-secret.yaml
```

## 4. Restart Deployment
```bash
kubectl rollout restart deployment payment-processor -n fintech-prod
```

# Verification

```bash
kubectl get pods -n fintech-prod -l app=payment-processor
argocd app sync payment-processor
```

# Prevention

1. Use dedicated service accounts for automation
2. Implement better secret management
3. Require DevOps approval for GitHub changes
4. Add monitoring for ImagePullBackOff events
"""
        else:
            return "No solution available for this problem."


if __name__ == "__main__":
    # Example usage
    agent = ExampleAgent()
    
    # In real usage, you'd get problem context from the eval framework
    problem = "k8s-github-secret-failure"
    solution = agent.solve_problem(problem)
    print(solution)