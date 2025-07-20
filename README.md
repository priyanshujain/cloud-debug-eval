# Cloud Debug Eval

Simple evaluation framework for testing agent performance on cloud infrastructure debugging problems using LLM-as-judge.

## Quick Start

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set your OpenAI API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run evaluation:**
   ```bash
   uv run python eval.py
   ```

4. **View reports:**
   Reports generated in `reports/` folder as Markdown files.

## Using Your Own Agent

Replace the agent import in `eval.py`:

```python
# Instead of:
from example_agent import ExampleAgent
agent = ExampleAgent()

# Use your agent:
from your_agent import YourAgent
agent = YourAgent()
```

## Agent Interface

```python
class YourAgent:
    def solve_problem(self, problem_context: str) -> str:
        """
        Solve a debugging problem given the full context.
        
        Args:
            problem_context: Formatted problem with logs, configs, etc.
            
        Returns:
            Solution string with root cause, diagnosis steps, solution, etc.
        """
        # Your implementation here
        return solution_string
```

## Structure

```
├── problems/                    # Problem directories
├── reports/                    # Generated evaluation reports (markdown)
├── src/evaluator.py            # Evaluation framework
├── example_agent.py           # Example external agent
└── eval.py                    # Run: python eval.py
```

## Evaluation

The LLM judge evaluates on three dimensions:

- **Diagnosis Accuracy (40%)**: How well did the agent identify the root cause?
- **Solution Correctness (40%)**: How correct and complete is the proposed fix?  
- **Investigation Quality (20%)**: How systematic and thorough is the debugging methodology?

## Adding Problems

1. Create directory under `problems/`
2. Include `problem.md`, `solution.md`, `logs/`, `configs/`
3. See `docs/problem-creation-guide.md` for details