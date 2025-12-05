from typing import Dict, Any, List, TypedDict, Annotated, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Define the state for our graph
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    city: Optional[str]
    weather_data: Optional[Dict[str, Any]]
    recommended_activities: Optional[List[str]]

class WeatherAgent:
    def __init__(self, use_real_weather: bool = False):
        """Initialize the WeatherAgent.
        
        Args:
            use_real_weather: If True, fetches real weather data from OpenWeatherMap.
                           If False, uses mock weather data.
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Get API keys from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_real_weather = use_real_weather
        
        if use_real_weather:
            self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
            if not self.weather_api_key:
                raise ValueError(
                    "OPENWEATHER_API_KEY environment variable not set. "
                    "Please create a .env file with your API key or set use_real_weather=False."
                )
        
        if not self.openai_api_key:
            print("Warning: OPENAI_API_KEY not set. Some features may be limited.")
        else:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
        
        # Initialize the graph
        self.workflow = StateGraph(AgentState)
        
        # Define the nodes
        self.workflow.add_node("receive_input", self.receive_input)
        self.workflow.add_node("get_weather", self.get_weather)
        self.workflow.add_node("recommend_activities", self.recommend_activities)
        self.workflow.add_node("format_response", self.format_response)
        
        # Define the edges
        self.workflow.add_edge("receive_input", "get_weather")
        self.workflow.add_edge("get_weather", "recommend_activities")
        self.workflow.add_edge("recommend_activities", "format_response")
        self.workflow.add_edge("format_response", END)
        
        # Set the entry point
        self.workflow.set_entry_point("receive_input")
        
        # Compile the graph
        self.app = self.workflow.compile()
    
    def receive_input(self, state: AgentState) -> AgentState:
        """Process the initial input from the user."""
        # Get the last message (user input)
        last_message = state["messages"][-1]
        
        # In a real implementation, we would parse the city from the message
        # For now, we'll use a simple approach
        city = "New York"  # Default city
        if isinstance(last_message, HumanMessage):
            # Simple extraction - in a real app, use more sophisticated parsing
            city = last_message.content.split("weather in ")[-1].split(" ")[0] or city
        
        return {"messages": state["messages"], "city": city}
    
    def _get_mock_weather(self, city: str) -> dict:
        """Generate mock weather data for testing."""
        import random
        from datetime import datetime
        
        # Different weather conditions to cycle through
        conditions = [
            {"main": "Clear", "description": "clear sky"},
            {"main": "Clouds", "description": "few clouds"},
            {"main": "Rain", "description": "light rain"},
            {"main": "Thunderstorm", "description": "thunderstorm with light rain"},
            {"main": "Snow", "description": "light snow"},
        ]
        
        # Get a consistent condition based on city name
        condition = conditions[hash(city) % len(conditions)]
        
        # Generate temperature based on condition
        if condition["main"] == "Snow":
            temp = random.uniform(-5, 2)  # Cold for snow
        elif condition["main"] == "Rain" or condition["main"] == "Thunderstorm":
            temp = random.uniform(5, 15)  # Mild for rain
        elif condition["main"] == "Clear":
            temp = random.uniform(18, 32)  # Warm for clear skies
        else:  # Clouds
            temp = random.uniform(10, 25)  # Moderate for clouds
            
        return {
            "weather": [condition],
            "main": {
                "temp": round(temp, 1),
                "feels_like": round(temp + random.uniform(-2, 2), 1),
                "temp_min": round(temp - random.uniform(0, 5), 1),
                "temp_max": round(temp + random.uniform(0, 5), 1),
                "pressure": random.randint(980, 1030),
                "humidity": random.randint(30, 90),
            },
            "visibility": random.randint(5000, 10000),
            "dt": int(datetime.now().timestamp()),
            "timezone": 0,
            "id": 0,
            "name": city,
            "cod": 200
        }
    
    def get_weather(self, state: AgentState) -> AgentState:
        """Fetch weather data for the given city."""
        city = state["city"]
        if not city:
            raise ValueError("No city provided for weather lookup")
        
        if self.use_real_weather:
            # Call OpenWeatherMap API
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url)
            
            if response.status_code != 200:
                raise ValueError(f"Error fetching weather data: {response.text}")
            
            weather_data = response.json()
        else:
            # Use mock data
            print(f"Using mock weather data for {city} (real weather is disabled)")
            weather_data = self._get_mock_weather(city)
        
        return {"messages": state["messages"], "city": city, "weather_data": weather_data}
    
    def recommend_activities(self, state: AgentState) -> AgentState:
        """Generate personalized activity recommendations using OpenAI's GPT-4 based on weather data."""
        if not state["weather_data"]:
            raise ValueError("No weather data available")
        
        weather_desc = state["weather_data"]["weather"][0]["description"]
        temp = state["weather_data"]["main"]["temp"]
        city = state["city"]
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_api_key)
            
            # Create a prompt for the AI
            prompt = f"""
            Based on the following weather information for {city}, suggest 3-5 specific and personalized activities.
            Be creative and consider the time of day and weather conditions.
            
            Weather in {city}:
            - Description: {weather_desc}
            - Temperature: {temp}°C
            
            Provide the activities as a JSON array of strings. Only return the JSON array, nothing else.
            Example: ["Activity 1", "Activity 2", "Activity 3"]
            """
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful travel assistant that suggests activities based on weather conditions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            # Extract and parse the response
            content = response.choices[0].message.content.strip()
            
            # Handle cases where the response might be wrapped in markdown code blocks
            if content.startswith('```json'):
                content = content[content.find('['):content.rfind(']')+1]
            elif content.startswith('```'):
                content = content[content.find('['):content.rfind(']')+1]
                
            activities = json.loads(content)
            
            if not isinstance(activities, list) or not all(isinstance(x, str) for x in activities):
                raise ValueError("Unexpected response format from AI")
                
        except Exception as e:
            print(f"Warning: Failed to get AI recommendations. Falling back to default activities. Error: {str(e)}")
            # Fallback to default activities if API call fails
            activities = self._get_default_activities(weather_desc, temp)
        
        return {
            "messages": state["messages"],
            "city": city,
            "weather_data": state["weather_data"],
            "recommended_activities": activities
        }
        
    def _get_default_activities(self, weather_desc: str, temp: float) -> List[str]:
        """Provide default activity recommendations if AI call fails."""
        if "rain" in weather_desc.lower():
            return ["Visit a museum", "Explore a local cafe", "Check out an indoor market"]
        elif temp > 25:
            return ["Go to the beach", "Have a picnic in the park", "Try outdoor swimming"]
        elif temp > 15:
            return ["Go for a scenic hike", "Visit a botanical garden", "Explore local markets"]
        else:
            return ["Visit a museum", "Enjoy a hot drink at a cozy cafe", "See a movie"]
    
    def format_response(self, state: AgentState) -> AgentState:
        """Format the final response with weather and recommendations."""
        if not state["weather_data"] or not state["recommended_activities"]:
            raise ValueError("Incomplete data to format response")
        
        weather = state["weather_data"]["weather"][0]["description"]
        temp = state["weather_data"]["main"]["temp"]
        city = state["city"]
        
        response = f"Weather in {city}: {weather}, {temp}°C\n\n"
        response += "Recommended activities:\n"
        for i, activity in enumerate(state["recommended_activities"], 1):
            response += f"{i}. {activity}\n"
        
        # In a real implementation, we would use the a2a protocol to format this
        a2a_response = {
            "type": "weather_recommendation",
            "city": city,
            "weather": {
                "description": weather,
                "temperature": temp,
                "unit": "celsius"
            },
            "recommended_activities": state["recommended_activities"]
        }
        
        # Add the response to the message history
        messages = state["messages"] + [AIMessage(content=json.dumps(a2a_response, indent=2))]
        
        return {
            "messages": messages,
            "city": city,
            "weather_data": state["weather_data"],
            "recommended_activities": state["recommended_activities"]
        }
    
    def process(self, input_message: str) -> str:
        """Process an input message and return the response."""
        # Initialize the state with the user's message
        initial_state = {
            "messages": [HumanMessage(content=input_message)],
            "city": None,
            "weather_data": None,
            "recommended_activities": None
        }
        
        # Run the graph
        result = self.app.invoke(initial_state)
        
        # Return the last message (the AI's response)
        return result["messages"][-1].content

# Example usage
if __name__ == "__main__":
    # Note: You'll need to set OPENWEATHER_API_KEY in your environment variables
    agent = WeatherAgent()
    
    # Example usage
    print("Weather Agent is running. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
            
        try:
            response = agent.process(user_input)
            print("\nAgent:", response, "\n")
        except Exception as e:
            print(f"Error: {str(e)}")
