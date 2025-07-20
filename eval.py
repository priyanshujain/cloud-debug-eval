#!/usr/bin/env python3
"""
Cloud debug evaluation - runs all problems and generates report.
"""

from src.evaluator import evaluate

# Import your agent here
from example_agent import ExampleAgent

if __name__ == "__main__":
    # Initialize agent and run evaluation
    agent = ExampleAgent()
    evaluate(agent.solve_problem, "example")