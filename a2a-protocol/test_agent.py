from weather_agent import WeatherAgent

def main():
    try:
        # Initialize the agent with real weather data
        # Set use_real_weather=False to use mock data instead
        agent = WeatherAgent(use_real_weather=True)
        
        # Test with a city
        city = "london"
        print(f"Getting weather for {city}...\n")
        
        # Get weather and recommendations
        # Using a more direct query format to avoid parsing issues
        response = agent.process(f"weather in {city}")
        
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
