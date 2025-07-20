# Solution: Kubernetes GitHub Secret Authentication Failure

## Root Cause

The GitHub user account `devops-automation` was removed from the GitHub organization during the security team's "cleanup" operation yesterday. This account was the owner of the Personal Access Token (PAT) used in the Kubernetes secret `github-registry-secret` for authenticating with GitHub Container Registry.

**Key Evidence**:
- GitHub API returns "Bad credentials" error (401 Unauthorized)
- The secret contains credentials for user `devops-automation` 
- Security team mentioned "cleaning up old GitHub accounts" yesterday
- All other services are working (suggesting this is account-specific, not infrastructure)

## Diagnosis Steps

### 1. Examine Pod Events
```bash
kubectl describe pod -n fintech-prod -l app=payment-processor
```
**Findings**: Pods failing with `ImagePullBackOff` and authentication errors when pulling from `ghcr.io`

### 2. Check Secret Configuration
```bash
kubectl get secret github-registry-secret -n fintech-prod -o yaml
echo "eyJhdXRocyI6eyJnaGNyLmlvIjp7InVzZXJuYW1lIjoiZGV2b3BzLWF1dG9tYXRpb24iLCJwYXNzd29yZCI6ImdocF9SNGw5VDBrZW5fQjNmNGtlX2V4YW1wbGVfdG9rZW4xMjM0NSIsImF1dGgiOiJaR1YyYjNCekxXRjFkRzl0WVhScGIyNDZaMmh3WDFJMGJEbFVNR3RsYmw5Q00yWTBhMlZmWlhoaGJYQnNaVjkwYjJ0bGJqRXlNelExIn19fQ==" | base64 -d
```
**Findings**: Secret contains credentials for user `devops-automation` with PAT starting with `ghp_R4l9T0ken_`

### 3. Test GitHub Authentication
```bash
curl -H "Authorization: token ghp_R4l9T0ken_B3f4ke_example_token12345" https://api.github.com/user
```
**Findings**: Returns `Bad credentials` error, confirming the token/account is invalid

### 4. Verify GitHub Organization Membership
- Check GitHub Enterprise admin panel for `devops-automation` user
- **Findings**: User account no longer exists in organization

### 5. Check Other Services
```bash
kubectl get pods -A | grep ImagePullBackOff
```
**Findings**: Only `payment-processor` affected, other services pulling from different registries or using different credentials

## Solution Steps

### 1. Create New Service Account in GitHub
```bash
# Via GitHub Enterprise admin panel or API:
# 1. Create new user: `k8s-registry-service`
# 2. Add to organization with appropriate permissions
# 3. Grant read access to Container Registry
```

### 2. Generate New Personal Access Token
```bash
# In GitHub settings for k8s-registry-service user:
# 1. Generate new PAT with scopes: read:packages, repo
# 2. Copy token (starts with ghp_)
```

### 3. Update Kubernetes Secret
```bash
# Create new docker config
kubectl create secret docker-registry github-registry-secret-new \
  --docker-server=ghcr.io \
  --docker-username=k8s-registry-service \
  --docker-password=ghp_NEW_TOKEN_HERE \
  --docker-email=devops@fintech-company.com \
  -n fintech-prod --dry-run=client -o yaml > new-secret.yaml

# Apply the new secret (replace existing)
kubectl delete secret github-registry-secret -n fintech-prod
kubectl apply -f new-secret.yaml
kubectl patch secret github-registry-secret-new -n fintech-prod -p '{"metadata":{"name":"github-registry-secret"}}'
```

### 4. Update Vault (for future automation)
```bash
# Update Vault secret path to use new credentials
vault kv put secret/github/registry \
  username=k8s-registry-service \
  token=ghp_NEW_TOKEN_HERE
```

### 5. Restart Deployment
```bash
kubectl rollout restart deployment payment-processor -n fintech-prod
```

## Verification

### 1. Check Pod Status
```bash
kubectl get pods -n fintech-prod -l app=payment-processor
# Should show all pods as Running
```

### 2. Verify Image Pull Success
```bash
kubectl describe pod -n fintech-prod -l app=payment-processor | grep -A5 -B5 "Successfully pulled"
```

### 3. Test End-to-End Deployment
```bash
# Trigger a new deployment through ArgoCD
argocd app sync payment-processor
argocd app wait payment-processor --health
```

### 4. Verify Application Health
```bash
kubectl port-forward svc/payment-processor 8080:8080 -n fintech-prod
curl localhost:8080/health
# Should return HTTP 200 with healthy status
```

## Prevention Measures

### 1. Use Service Accounts Instead of Personal Accounts
- Create dedicated service accounts for automation
- Avoid using personal GitHub accounts for production systems
- Document all service accounts and their purposes

### 2. Implement Better Secret Management
- Use Vault or AWS Secrets Manager for secret rotation
- Set up automated secret rotation for PATs
- Monitor secret expiration dates

### 3. Improve Change Communication
- Require DevOps approval for GitHub organization changes
- Maintain inventory of service accounts and their usage
- Set up alerts for authentication failures

### 4. Add Monitoring and Alerting
```bash
# Add Prometheus alert for ImagePullBackOff
- alert: ImagePullBackOff
  expr: kube_pod_container_status_waiting_reason{reason="ImagePullBackOff"} > 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has ImagePullBackOff"
```

### 5. Documentation Updates
- Document all GitHub service accounts and their purposes
- Create runbook for GitHub authentication issues
- Update incident response procedures

## Time to Resolution
- **Root cause identification**: 15-20 minutes
- **Solution implementation**: 10-15 minutes  
- **Verification**: 5-10 minutes
- **Total**: 30-45 minutes

This incident highlights the importance of treating service accounts as critical infrastructure and coordinating changes that affect authentication systems across teams.