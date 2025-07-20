#!/usr/bin/env python3
"""
Cloud Debug Eval - LLM-as-judge evaluation for cloud debugging solutions.
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Problem:
    """Represents a cloud debugging problem."""

    name: str
    path: Path
    problem_md: str
    solution_md: str
    logs: Dict[str, str]
    configs: Dict[str, str]

    @classmethod
    def load(cls, problem_path: Path) -> "Problem":
        """Load a problem from its directory."""
        problem_md = (problem_path / "problem.md").read_text()
        solution_md = (problem_path / "solution.md").read_text()

        # Load all logs
        logs = {}
        logs_dir = problem_path / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                logs[log_file.name] = log_file.read_text()

        # Load all configs
        configs = {}
        configs_dir = problem_path / "configs"
        if configs_dir.exists():
            for config_file in configs_dir.glob("*.yaml"):
                configs[config_file.name] = config_file.read_text()

        return cls(
            name=problem_path.name,
            path=problem_path,
            problem_md=problem_md,
            solution_md=solution_md,
            logs=logs,
            configs=configs,
        )

    def get_context_for_agent(self) -> str:
        """Get formatted context to send to external agent."""
        context = f"# Cloud Infrastructure Debugging Problem\n\n"
        context += f"{self.problem_md}\n\n"

        if self.logs:
            context += "## Available Logs\n\n"
            for log_name, log_content in self.logs.items():
                context += f"### {log_name}\n```\n{log_content}\n```\n\n"

        if self.configs:
            context += "## Configuration Files\n\n"
            for config_name, config_content in self.configs.items():
                context += f"### {config_name}\n```yaml\n{config_content}\n```\n\n"

        context += """
## Your Task
As an experienced cloud engineer, analyze this problem and provide:

1. **Root Cause Analysis**: What is the underlying issue causing this problem?
2. **Diagnosis Steps**: What specific steps would you take to investigate and confirm the root cause?
3. **Solution**: What are the specific steps to fix this issue?
4. **Verification**: How would you verify that your solution worked?
5. **Prevention**: What measures would prevent this from happening again?

Please be specific with commands, configurations, and procedures.
"""
        return context


@dataclass
class EvaluationResult:
    """Results from LLM judge evaluation."""

    problem_name: str
    agent_name: str
    timestamp: str
    diagnosis_accuracy: int  # 0-100
    solution_correctness: int  # 0-100
    investigation_quality: int  # 0-100
    overall_score: int  # 0-100
    agent_solution: str
    expected_solution: str
    judge_feedback: str
    judge_reasoning: str
    judge_model: str


class LLMJudge:
    """LLM-as-judge for evaluating debugging solutions."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def evaluate_solution(
        self, problem: Problem, agent_solution: str, agent_name: str = "unknown"
    ) -> EvaluationResult:
        """Evaluate agent solution against expected solution using LLM judge."""

        judge_prompt = self._create_judge_prompt(problem, agent_solution)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_judge_system_prompt()},
                    {"role": "user", "content": judge_prompt},
                ],
                max_tokens=1500,
                temperature=0.1,
            )

            judge_response = response.choices[0].message.content
            return self._parse_judge_response(
                problem, agent_solution, agent_name, judge_response
            )

        except Exception as e:
            return EvaluationResult(
                problem_name=problem.name,
                agent_name=agent_name,
                timestamp=datetime.now().isoformat(),
                diagnosis_accuracy=0,
                solution_correctness=0,
                investigation_quality=0,
                overall_score=0,
                agent_solution=agent_solution,
                expected_solution=problem.solution_md,
                judge_feedback=f"Error during evaluation: {str(e)}",
                judge_reasoning="",
                judge_model=self.model,
            )

    def _get_judge_system_prompt(self) -> str:
        """System prompt for LLM judge."""
        return """You are an expert cloud infrastructure engineer and evaluation judge with 15+ years of experience. 

Your task is to evaluate debugging solutions by comparing an agent's solution against the expected solution for cloud infrastructure problems.

You should score on three dimensions:
1. **Diagnosis Accuracy (0-100)**: How well did the agent identify the root cause?
2. **Solution Correctness (0-100)**: How correct and complete is the proposed fix?
3. **Investigation Quality (0-100)**: How systematic and thorough is the debugging methodology?

Be fair but rigorous. Consider that there may be multiple valid approaches, but focus on:
- Technical accuracy
- Operational feasibility  
- Completeness of solution
- Quality of debugging process
- Risk considerations

Provide your response in this exact JSON format:
{
    "diagnosis_accuracy": <score 0-100>,
    "solution_correctness": <score 0-100>, 
    "investigation_quality": <score 0-100>,
    "reasoning": "<detailed explanation of your scoring>",
    "feedback": "<constructive feedback for improvement>"
}"""

    def _create_judge_prompt(self, problem: Problem, agent_solution: str) -> str:
        """Create the evaluation prompt for the judge."""
        return f"""# Evaluation Task

## Problem Context
{problem.problem_md}

## Expected Solution (Ground Truth)
{problem.solution_md}

## Agent's Solution (To Evaluate)
{agent_solution}

## Your Task
Compare the agent's solution against the expected solution and evaluate on:

1. **Diagnosis Accuracy**: Did the agent correctly identify the root cause?
2. **Solution Correctness**: Is the proposed solution technically sound and complete?
3. **Investigation Quality**: Does the agent show good debugging methodology?

Consider:
- Technical accuracy of commands and procedures
- Completeness of the solution
- Risk assessment and prevention measures
- Clarity and systematicness of approach
- Whether the solution would actually work in practice

Score each dimension 0-100 and provide detailed reasoning."""

    def _parse_judge_response(
        self,
        problem: Problem,
        agent_solution: str,
        agent_name: str,
        judge_response: str,
    ) -> EvaluationResult:
        """Parse judge response and create evaluation result."""
        try:
            # Try to extract JSON from response
            start_idx = judge_response.find("{")
            end_idx = judge_response.rfind("}") + 1

            if start_idx != -1 and end_idx != -1:
                json_str = judge_response[start_idx:end_idx]
                judge_data = json.loads(json_str)

                diagnosis = judge_data.get("diagnosis_accuracy", 0)
                solution = judge_data.get("solution_correctness", 0)
                investigation = judge_data.get("investigation_quality", 0)
                reasoning = judge_data.get("reasoning", "No reasoning provided")
                feedback = judge_data.get("feedback", "No feedback provided")

                # Calculate overall score (weighted average)
                overall = int(diagnosis * 0.4 + solution * 0.4 + investigation * 0.2)

                return EvaluationResult(
                    problem_name=problem.name,
                    agent_name=agent_name,
                    timestamp=datetime.now().isoformat(),
                    diagnosis_accuracy=int(diagnosis),
                    solution_correctness=int(solution),
                    investigation_quality=int(investigation),
                    overall_score=overall,
                    agent_solution=agent_solution,
                    expected_solution=problem.solution_md,
                    judge_feedback=feedback,
                    judge_reasoning=reasoning,
                    judge_model=self.model,
                )
            else:
                raise ValueError("No JSON found in judge response")

        except Exception as e:
            # Fallback if JSON parsing fails
            return EvaluationResult(
                problem_name=problem.name,
                agent_name=agent_name,
                timestamp=datetime.now().isoformat(),
                diagnosis_accuracy=50,
                solution_correctness=50,
                investigation_quality=50,
                overall_score=50,
                agent_solution=agent_solution,
                expected_solution=problem.solution_md,
                judge_feedback=f"Failed to parse judge response: {str(e)}",
                judge_reasoning=judge_response,
                judge_model=self.model,
            )


class CloudDebugEvaluator:
    """Main evaluator orchestrator."""

    def __init__(self, api_key: Optional[str] = None, judge_model: str = "gpt-4"):
        self.judge = LLMJudge(api_key, judge_model)
        self.problems_dir = Path("problems")
        self.reports_dir = Path("reports")

    def evaluate_with_agent(
        self,
        problem_name: str,
        agent_function: Callable[[str], str],
        agent_name: str = "unknown",
    ) -> EvaluationResult:
        """Evaluate a problem by running agent and then judging the result."""
        problem_path = self.problems_dir / problem_name
        problem = Problem.load(problem_path)

        # Get problem context for agent
        problem_context = problem.get_context_for_agent()

        # Run external agent
        print(f"Running agent '{agent_name}' on problem '{problem.name}'...")
        agent_solution = agent_function(problem_context)

        # Evaluate with judge
        print(f"Evaluating solution with {self.judge.model} judge...")
        result = self.judge.evaluate_solution(problem, agent_solution, agent_name)

        return result

    def evaluate_all_problems(
        self, agent_function: Callable[[str], str], agent_name: str = "unknown"
    ) -> List[EvaluationResult]:
        """Evaluate all problems with given agent."""
        results = []
        for problem_dir in self.problems_dir.iterdir():
            if problem_dir.is_dir() and (problem_dir / "problem.md").exists():
                result = self.evaluate_with_agent(
                    problem_dir.name, agent_function, agent_name
                )
                results.append(result)
        return results

    def generate_report(self, results: List[EvaluationResult]):
        """Generate evaluation report."""
        self.reports_dir.mkdir(exist_ok=True)

        # Generate timestamp for report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        agent_name = results[0].agent_name if results else "unknown"

        # Markdown report
        md_path = self.reports_dir / f"eval_report_{agent_name}_{timestamp}.md"
        md_content = self._generate_md_report(results)
        with open(md_path, "w") as f:
            f.write(md_content)
        return md_path

    def _generate_md_report(self, results: List[EvaluationResult]) -> str:
        """Generate Markdown report."""
        if not results:
            return "# No results to report"

        agent_name = results[0].agent_name
        timestamp = results[0].timestamp
        avg_score = sum(r.overall_score for r in results) / len(results)

        md = f"""# Cloud Debug Eval Report

**Agent:** {agent_name}  
**Timestamp:** {timestamp}  
**Problems Evaluated:** {len(results)}  
**Average Score:** {avg_score:.1f}/100

## Summary

| Problem | Overall Score | Diagnosis | Solution | Investigation |
|---------|---------------|-----------|----------|---------------|
"""

        for result in results:
            md += f"| {result.problem_name} | {result.overall_score}/100 | {result.diagnosis_accuracy}/100 | {result.solution_correctness}/100 | {result.investigation_quality}/100 |\n"

        md += "\n## Detailed Results\n\n"

        # Detailed results
        for result in results:
            md += f"""### {result.problem_name}

**Overall Score:** {result.overall_score}/100

**Scores:**
- Diagnosis Accuracy: {result.diagnosis_accuracy}/100
- Solution Correctness: {result.solution_correctness}/100  
- Investigation Quality: {result.investigation_quality}/100

**Judge Feedback:**
{result.judge_feedback}

**Judge Reasoning:**
{result.judge_reasoning}
---

"""

        return md


def evaluate(agent_function: Callable[[str], str], agent_name: str = "unknown"):
    """Evaluate all problems and generate report."""
    evaluator = CloudDebugEvaluator()
    results = evaluator.evaluate_all_problems(agent_function, agent_name)
    evaluator.generate_report(results)

    print(f"\n=== Summary for {len(results)} problems ===")
    avg_score = sum(r.overall_score for r in results) / len(results) if results else 0
    print(f"Average Score: {avg_score:.1f}/100")

    for result in results:
        print(f"{result.problem_name}: {result.overall_score}/100")
