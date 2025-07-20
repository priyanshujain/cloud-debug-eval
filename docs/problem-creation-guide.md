# Problem Creation Guide

## Overview

This guide explains how to create realistic cloud debugging problems for the evaluation. Each problem should be based on real-world incidents and include all the artifacts an engineer would have during actual debugging.

## Problem Structure

Each problem lives in its own folder under `problems/` with this structure:

```
problems/your-problem-name/
├── problem.md          # Problem description and context
├── solution.md         # Expected diagnosis and solution steps
├── logs/              # All log files (.log extension)
├── configs/           # Configuration files (.yaml extension)
└── metrics/           # Performance data and metrics (.log extension)
```

## File Guidelines

### problem.md
- **Title**: Clear, descriptive problem title
- **Context**: Business scenario, team structure, time pressure
- **Systems Involved**: List all systems/technologies involved
- **Problem Statement**: What's failing, when it started, user impact
- **Available Information**: What tools/access the engineer has
- **Constraints**: Time pressure, business impact, compliance requirements

### solution.md
- **Root Cause**: The actual underlying issue
- **Diagnosis Steps**: How to systematically identify the problem
- **Solution Steps**: Specific commands/actions to fix it
- **Verification**: How to confirm the fix worked
- **Prevention**: Steps to prevent recurrence

### logs/
- Use `.log` extension for all log files
- Include realistic timestamps and log formats
- Sanitize any sensitive information
- Include both relevant and some irrelevant logs (realistic noise)

### configs/
- Use `.yaml` extension for all configuration files
- Include both working and broken configurations
- Show the actual problematic settings
- Include related configurations that provide context

### metrics/
- Performance data, monitoring outputs
- Use `.log` extension for consistency
- Include before/during/after incident data if relevant

## Problem Quality Checklist

### ✅ Realism
- [ ] Based on actual production incident
- [ ] Realistic infrastructure setup
- [ ] Authentic error messages and logs
- [ ] Proper tool outputs and formats
- [ ] Reasonable time constraints

### ✅ Multi-System Complexity
- [ ] Involves 2+ systems/technologies
- [ ] Requires understanding system interactions
- [ ] Shows realistic dependency chains
- [ ] Includes cross-team/service boundaries

### ✅ Educational Value
- [ ] Teaches transferable debugging skills
- [ ] Shows proper investigation methodology
- [ ] Includes common debugging pitfalls
- [ ] Demonstrates industry best practices

### ✅ Completeness
- [ ] All necessary artifacts included
- [ ] Problem is solvable with provided information
- [ ] Multiple valid solution paths acknowledged
- [ ] Clear success criteria defined

## Difficulty Levels

### Level 1: Associate (0-2 years)
- Single system failures with clear error messages
- Well-documented solutions
- Limited cross-system dependencies
- 30-60 minutes to solve

### Level 2: Mid-Level (2-5 years)
- 2-3 system interactions
- Some misleading symptoms
- Requires log analysis and correlation
- 1-2 hours to solve

### Level 3: Senior (5-8 years)
- Complex multi-system failures
- Subtle configuration issues
- Performance and scaling problems
- 2-4 hours to solve

### Level 4: Staff (8-12 years)
- Cross-cloud or hybrid scenarios
- Security and compliance considerations
- Business impact assessment required
- 4-8 hours to solve

### Level 5: Principal (12+ years)
- Organization-wide system failures
- Multiple valid approaches with trade-offs
- Strategic decision making required
- Variable time depending on approach

## Example Problem Types

### Authentication Chain Failures
- OAuth token issues across services
- Certificate expiration cascades
- RBAC misconfigurations

### Network Connectivity Issues
- DNS resolution problems
- Firewall rule conflicts
- Load balancer misconfigurations
- VPC peering issues

### Storage and Data Problems
- Database connectivity issues
- Persistent volume mounting failures
- Backup and restore problems
- Data consistency issues

### Performance and Scaling
- Resource constraint cascades
- Auto-scaling configuration issues
- Cache invalidation problems
- Database performance degradation

### Security Incidents
- Credential rotation failures
- Security group misconfigurations
- Compliance violation scenarios
- Access control problems

## Contributing Your Problem

1. Create a new folder under `problems/` with a descriptive name
2. Follow the file structure and naming conventions
3. Fill out all required files (problem.md, solution.md)
4. Include realistic artifacts (logs, configs, metrics)
5. Test that the problem is solvable with provided information
6. Use the quality checklist to self-review

## Best Practices

### Making Problems Realistic
- Use actual error messages from real systems
- Include realistic timestamps and UUIDs
- Add some red herrings and irrelevant information
- Show the messy reality of production environments

### Sanitizing Sensitive Data (We will create a script to do this)
- Replace real IPs with RFC 1918 addresses
- Use example.com for domain names
- Replace real API keys with dummy values
- Anonymize company and team names

### Writing Clear Solutions
- Explain the reasoning behind each step
- Include alternative approaches where applicable
- Show verification commands
- Explain why other approaches might not work

Remember: The goal is to create problems that feel like real incidents an experienced engineer would encounter in production environments.