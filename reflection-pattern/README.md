# Reflection Agentic Pattern

A Streamlit application demonstrating the **Reflection Agentic Pattern** using a Producer-Critic feedback loop for iterative code refinement.

## 🎯 Overview

The Reflection Pattern is an agentic design pattern that involves two key agents working together:

1. **Producer Agent**: Generates initial Python code based on user requirements
2. **Critic Agent**: Acts as a Senior Staff Engineer, evaluating the code for logic, efficiency, PEP8 compliance, and best practices
3. **Feedback Loop**: The Producer refines the code based on the Critic's feedback through multiple iterations

This iterative process continues until the code is approved by the Critic or the maximum number of iterations is reached.

## 🏗️ Architecture

```
User Prompt → Producer Agent → Generated Code
                    ↑                ↓
                    |          Critic Agent
                    |                ↓
                    └──── Feedback ──┘
```

## 🚀 Features

- **Interactive UI**: Clean Streamlit interface with real-time feedback
- **Configurable Iterations**: Adjust the maximum number of refinement cycles
- **Thought Process Visualization**: View each iteration's draft and critique
- **Syntax Highlighting**: Final code displayed with proper formatting
- **Download Capability**: Export the generated code as a Python file
- **Environment Variable Security**: No hardcoded API keys

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/drkarim/Multi-Agentic-Patterns.git
cd Multi-Agentic-Patterns/reflection-pattern
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🔑 Setting Up the OpenAI API Key

The application requires an OpenAI API key to function. **Do not hardcode your API key in the code.**

### On Windows (PowerShell)

```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

### On Windows (Command Prompt)

```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

### On macOS/Linux (Bash/Zsh)

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### Using a .env File (Recommended for Development)

Create a `.env` file in the `reflection-pattern/` directory:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

The application will automatically load this file using `python-dotenv`.

## ▶️ Running the Application

After setting the environment variable, run:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## 📖 Usage Guide

### Step 1: Configure Settings

- Use the sidebar to adjust the **Max Iterations** (1-5)
- Verify that the OpenAI API key is detected (green checkmark)

### Step 2: Enter Your Request

In the main text area, describe the Python code you want to generate. Examples:

- "Create a function to calculate Fibonacci numbers using memoization"
- "Write a class for managing a simple todo list with add, remove, and list operations"
- "Implement a binary search algorithm with proper error handling"

### Step 3: Generate Code

Click the **🚀 Generate Code** button to start the reflection process.

### Step 4: Review the Process

- **Metrics**: View the total iterations, status, and max allowed
- **Thought Process**: Expand each iteration to see the draft code and critique
- **Final Code**: Review the approved or final version with syntax highlighting

### Step 5: Download

Use the **📥 Download Code** button to save the generated code as a `.py` file.

## 🧪 Example Prompts

Try these prompts to see the Reflection Pattern in action:

1. **Email Validator**
   ```
   Create a function to validate email addresses using regex with proper error handling
   ```

2. **Fibonacci with Memoization**
   ```
   Write a function to calculate Fibonacci numbers using memoization for efficiency
   ```

3. **Binary Search**
   ```
   Implement a binary search algorithm that handles edge cases and returns the index
   ```

4. **Execution Timer Decorator**
   ```
   Create a decorator that logs the execution time of any function it wraps
   ```

## 📁 Project Structure

```
reflection-pattern/
├── app.py              # Main Streamlit application
├── agents.py           # Producer and Critic agent implementations
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .env               # (Optional) Environment variables
```

## 🛠️ Technical Details

### Agent Implementation

- **Framework**: LangChain with OpenAI's GPT models
- **Producer Agent**: Uses `temperature=0.7` for creative code generation
- **Critic Agent**: Uses `temperature=0.3` for consistent, analytical feedback
- **Pattern**: LCEL (LangChain Expression Language) for chain composition

### Models Used

- Default: `gpt-4.1-mini` (configurable in `agents.py`)
- Can be changed to `gpt-4`, `gpt-3.5-turbo`, or other OpenAI models

### Security

- API keys are retrieved from environment variables only
- No hardcoded credentials in the codebase
- `.env` file support for local development (should be added to `.gitignore`)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of the Multi-Agentic-Patterns repository. Please refer to the main repository for license information.

## 🐛 Troubleshooting

### "OpenAI API Key not found" Error

**Solution**: Ensure you've set the `OPENAI_API_KEY` environment variable before running the app.

### Import Errors

**Solution**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Connection Errors

**Solution**: Check your internet connection and verify your OpenAI API key is valid and has available credits.

## 📚 Learn More

- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Agentic Design Patterns](https://www.deeplearning.ai/the-batch/)

## 👥 Authors

- **Repository Owner**: drkarim
- **Pattern Implementation**: Manus AI

## 🙏 Acknowledgments

- LangChain team for the excellent framework
- Streamlit for the intuitive UI library
- OpenAI for the powerful language models
