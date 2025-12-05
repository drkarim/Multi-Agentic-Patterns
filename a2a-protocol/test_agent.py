from weather_agent import WeatherAgent

def main():
    try:
        # Initialize the agent
        agent = WeatherAgent()
        
        # Test with a city
        city = "London"
        print(f"Getting weather for {city}...\n")
        
        # Get weather and recommendations
        response = agent.process(f"What's the weather like in {city}?")
        
        # Print the response
        print("Agent Response:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nMake sure you have:")
        print("1. Created a .env file with your API keys")
        print("2. Activated the virtual environment (source .venv/bin/activate)")
        print("3. Installed the requirements (pip install -r requirements.txt)")

if __name__ == "__main__":
    main()
