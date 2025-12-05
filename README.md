# Multi-Agent Patterns with LangChain and LangGraph

This repository contains implementations of various multi-agent patterns using LangChain and LangGraph. Each pattern is implemented in its own directory with a dedicated README explaining its design and usage.

## Available Patterns

### 1. Plan-and-Execute Agent
**Directory**: [planning-agent/](planning-agent/)

A two-agent system where:
- **Planner**: Breaks down complex tasks into manageable steps
- **Executor**: Carries out each step and reports back

The system operates in a loop, with the Planner refining the plan after each execution step until the task is complete. This pattern is particularly effective for complex, multi-step tasks that may require adaptation based on intermediate results.

[Read more about the Plan-and-Execute pattern →](planning-agent/README.md)

### 2. Agent with a2a Protocol
**Directory**: [a2a-protocol/](a2a-protocol/)

A weather agent that demonstrates the Agent-to-Agent (a2a) communication protocol, featuring:
- **Mock Data Support**: Test without API keys using realistic mock weather data
- **OpenAI Integration**: Get AI-powered activity recommendations based on weather
- **Flexible Configuration**: Toggle between real and mock data with a simple flag

The agent follows a clear workflow from input processing to response formatting, making it a great example of a single-agent system with well-defined responsibilities.

[Explore the a2a Protocol Agent →](a2a-protocol/README.md)

## Getting Started

Each pattern has its own setup instructions and requirements. Please refer to the individual pattern's README for specific details.

## Prerequisites

- Python 3.8+
- [Poetry](https://python-poetry.org/) (recommended) or pip
- API keys for required services (OpenAI, etc.)

## Contributing

Feel free to contribute new patterns or improvements to existing ones. Please follow the existing structure and include proper documentation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Rashed Karim

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Acknowledgements

- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [OpenAI](https://openai.com/)
