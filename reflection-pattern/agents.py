"""
Reflection Agentic Pattern Implementation
This module implements the Producer-Critic pattern for iterative code refinement.
"""

import os
from typing import Dict, List, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage


class ProducerAgent:
    """
    Producer Agent: Generates initial Python code or technical content based on user prompts.
    """
    
    def __init__(self, model_name: str = "gpt-4.1-mini", temperature: float = 0.7):
        """
        Initialize the Producer Agent with an LLM.
        
        Args:
            model_name: The name of the OpenAI model to use
            temperature: Controls randomness in generation (0.0 to 1.0)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Python developer. Generate clean, efficient, and well-documented Python code based on user requirements.
Follow PEP8 style guidelines and include docstrings for functions and classes.
Only return the code without any additional explanation or markdown formatting."""),
            ("human", "{user_prompt}")
        ])
    
    def generate(self, user_prompt: str, feedback: str = None) -> str:
        """
        Generate Python code based on user prompt and optional feedback.
        
        Args:
            user_prompt: The original user requirement
            feedback: Optional feedback from the Critic for refinement
            
        Returns:
            Generated Python code as a string
        """
        if feedback:
            enhanced_prompt = f"""Original Request: {user_prompt}

Feedback from Senior Staff Engineer:
{feedback}

Please refine the code based on this feedback while maintaining the original requirements."""
        else:
            enhanced_prompt = user_prompt
        
        chain = self.prompt_template | self.llm
        response = chain.invoke({"user_prompt": enhanced_prompt})
        
        return response.content


class CriticAgent:
    """
    Critic Agent: Acts as a Senior Staff Engineer to evaluate and provide feedback on code.
    """
    
    def __init__(self, model_name: str = "gpt-4.1-mini", temperature: float = 0.3):
        """
        Initialize the Critic Agent with an LLM.
        
        Args:
            model_name: The name of the OpenAI model to use
            temperature: Controls randomness (lower for more consistent critique)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a Senior Staff Engineer conducting a thorough code review.
Evaluate the provided Python code for:
1. Logic correctness and efficiency
2. PEP8 compliance and code style
3. Error handling and edge cases
4. Documentation quality
5. Best practices and design patterns

Provide constructive feedback with specific suggestions for improvement.
If the code is excellent and requires no changes, respond with "APPROVED: The code meets all quality standards."
Otherwise, provide detailed feedback on what needs to be improved."""),
            ("human", """Original Request: {user_prompt}

Generated Code:
```python
{code}
```

Please review this code and provide feedback.""")
        ])
    
    def critique(self, user_prompt: str, code: str) -> Tuple[bool, str]:
        """
        Critique the generated code and provide feedback.
        
        Args:
            user_prompt: The original user requirement
            code: The generated code to review
            
        Returns:
            Tuple of (is_approved, feedback_message)
        """
        chain = self.prompt_template | self.llm
        response = chain.invoke({
            "user_prompt": user_prompt,
            "code": code
        })
        
        feedback = response.content
        is_approved = feedback.startswith("APPROVED:")
        
        return is_approved, feedback


class ReflectionPattern:
    """
    Orchestrates the Reflection Pattern with Producer and Critic agents.
    """
    
    def __init__(self, max_iterations: int = 3):
        """
        Initialize the Reflection Pattern orchestrator.
        
        Args:
            max_iterations: Maximum number of refinement iterations
        """
        self.producer = ProducerAgent()
        self.critic = CriticAgent()
        self.max_iterations = max_iterations
    
    def execute(self, user_prompt: str) -> Dict:
        """
        Execute the reflection pattern: generate, critique, refine.
        
        Args:
            user_prompt: The user's code generation request
            
        Returns:
            Dictionary containing the process history and final code
        """
        history = []
        current_code = None
        feedback = None
        
        for iteration in range(self.max_iterations):
            # Producer generates/refines code
            current_code = self.producer.generate(user_prompt, feedback)
            
            # Critic evaluates the code
            is_approved, feedback = self.critic.critique(user_prompt, current_code)
            
            # Record this iteration
            history.append({
                "iteration": iteration + 1,
                "code": current_code,
                "feedback": feedback,
                "approved": is_approved
            })
            
            # If approved, break the loop
            if is_approved:
                break
        
        return {
            "final_code": current_code,
            "history": history,
            "total_iterations": len(history),
            "approved": history[-1]["approved"] if history else False
        }
