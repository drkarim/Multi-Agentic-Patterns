"""
Reflection Agentic Pattern - Streamlit Application
Demonstrates the Producer-Critic pattern for iterative code refinement.
"""

import streamlit as st
from agents import ReflectionPattern
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Reflection Agentic Pattern",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .iteration-badge {
        background-color: #E3F2FD;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        color: #1976D2;
    }
    .approved-badge {
        background-color: #C8E6C9;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        color: #388E3C;
    }
    .rejected-badge {
        background-color: #FFCDD2;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        color: #D32F2F;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔄 Reflection Agentic Pattern</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Producer-Critic Pattern for Iterative Code Refinement</div>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Check for API key
    api_key_status = os.getenv("OPENAI_API_KEY")
    if api_key_status:
        st.success("✅ OpenAI API Key detected")
    else:
        st.error("❌ OpenAI API Key not found")
        st.info("Please set the OPENAI_API_KEY environment variable")
    
    st.divider()
    
    # Max iterations setting
    max_iterations = st.slider(
        "Max Iterations",
        min_value=1,
        max_value=5,
        value=3,
        help="Maximum number of refinement iterations"
    )
    
    st.divider()
    
    # Pattern explanation
    with st.expander("ℹ️ About the Pattern"):
        st.markdown("""
        **Reflection Agentic Pattern** involves:
        
        1. **Producer Agent**: Generates initial code based on your prompt
        2. **Critic Agent**: Acts as a Senior Staff Engineer, reviewing the code
        3. **Feedback Loop**: The Producer refines the code based on critique
        
        This iterative process continues until the code is approved or max iterations are reached.
        """)
    
    # Example prompts
    with st.expander("💡 Example Prompts"):
        st.markdown("""
        - "Create a function to calculate Fibonacci numbers using memoization"
        - "Write a class for managing a simple todo list with add, remove, and list operations"
        - "Implement a binary search algorithm with proper error handling"
        - "Create a decorator that logs function execution time"
        """)

# Main content area
st.header("📝 Code Generation Request")

# User input
user_prompt = st.text_area(
    "Enter your code generation request:",
    height=150,
    placeholder="Example: Create a function to validate email addresses using regex...",
    help="Describe what Python code you want the Producer agent to generate"
)

# Generate button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("🚀 Generate Code", type="primary", use_container_width=True)

# Process generation
if generate_button:
    if not user_prompt.strip():
        st.warning("⚠️ Please enter a code generation request")
    elif not api_key_status:
        st.error("❌ OpenAI API Key is not set. Please set the OPENAI_API_KEY environment variable.")
    else:
        with st.spinner("🔄 Running Reflection Pattern..."):
            try:
                # Initialize and execute the pattern
                reflection = ReflectionPattern(max_iterations=max_iterations)
                result = reflection.execute(user_prompt)
                
                # Store result in session state
                st.session_state['result'] = result
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state['result'] = None

# Display results if available
if 'result' in st.session_state and st.session_state['result']:
    result = st.session_state['result']
    
    st.divider()
    st.header("🎯 Results")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Iterations", result['total_iterations'])
    with col2:
        status = "✅ Approved" if result['approved'] else "⚠️ Max Iterations Reached"
        st.metric("Status", status)
    with col3:
        st.metric("Max Allowed", max_iterations)
    
    st.divider()
    
    # Thought process - show each iteration
    st.header("🧠 Thought Process")
    
    for idx, iteration_data in enumerate(result['history']):
        iteration_num = iteration_data['iteration']
        code = iteration_data['code']
        feedback = iteration_data['feedback']
        approved = iteration_data['approved']
        
        with st.expander(f"**Iteration {iteration_num}** {'✅ Approved' if approved else '🔄 Needs Refinement'}", expanded=(idx == 0)):
            # Show the generated code
            st.subheader(f"📄 Draft {iteration_num}")
            st.code(code, language="python", line_numbers=True)
            
            st.divider()
            
            # Show the critique
            st.subheader(f"🔍 Critique {iteration_num}")
            if approved:
                st.success(feedback)
            else:
                st.warning(feedback)
    
    st.divider()
    
    # Final code with syntax highlighting
    st.header("✨ Final Code")
    
    if result['approved']:
        st.success("✅ Code approved by the Critic Agent!")
    else:
        st.info("ℹ️ Maximum iterations reached. The code may benefit from further refinement.")
    
    st.code(result['final_code'], language="python", line_numbers=True)
    
    # Download button
    st.download_button(
        label="📥 Download Code",
        data=result['final_code'],
        file_name="generated_code.py",
        mime="text/plain",
        use_container_width=True
    )

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Built with ❤️ using Streamlit and LangChain</p>
    <p>Reflection Agentic Pattern Demo</p>
</div>
""", unsafe_allow_html=True)
