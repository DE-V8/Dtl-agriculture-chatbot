"""
LLM Handler for Agriculture Chat Interface

This module provides LLM integration using a local server for more natural conversations.
"""

import requests
from typing import List, Dict, Generator, Optional, Union
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class LLMHandler:
    def __init__(self):
        # Local server configuration
        self.base_url = "http://192.168.215.138:1234"  # LM Studio server URL
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 5  # Keep last 5 exchanges for context
        self.max_retries = 3
        self.session = self._setup_session()
        self.test_connection()
        
    def _setup_session(self) -> requests.Session:
        """Setup a session with retry mechanism"""
        session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        
        # Mount the adapter to the session
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
        
    def test_connection(self) -> bool:
        """Test connection to the local server"""
        try:
            print(f"Testing connection to {self.base_url}...")
            response = self.session.get(self.base_url, timeout=5)
            print(f"Server response status: {response.status_code}")
            
            if response.status_code == 200:
                print("Successfully connected to local server!")
                return True
            else:
                print(f"Server returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("Could not connect to local server. Please make sure the server is running.")
            return False
        except requests.exceptions.Timeout:
            print("Connection to server timed out.")
            return False
        except Exception as e:
            print(f"Error testing connection: {e}")
            return False
            
    def add_to_history(self, user_message: str, assistant_message: str):
        """Add a message exchange to conversation history"""
        self.conversation_history.append({
            "user": user_message,
            "assistant": assistant_message,
            "timestamp": time.time()
        })
        # Keep only the last max_history exchanges
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
            
    def summarize_conversation(self) -> str:
        """Summarize the conversation history if it gets too long"""
        if len(self.conversation_history) < 2:
            return ""
            
        summary = "Previous conversation summary:\n"
        for exchange in self.conversation_history[:-1]:  # Exclude the most recent exchange
            summary += f"- User asked about {exchange['user'][:50]}...\n"
            summary += f"- Assistant provided information about {exchange['assistant'][:50]}...\n"
        return summary
            
    def get_messages(self, user_message: str, context: str = "", data: pd.DataFrame = None) -> List[Dict[str, str]]:
        """Get messages in OpenAI chat format"""
        messages = [
            {
                "role": "system",
                "content": "You are an agricultural data analysis assistant. You help with analyzing agricultural data, providing insights, and making recommendations."
            }
        ]
        
        # Add data context if provided
        if data is not None:
            data_context = f"Available data columns: {', '.join(data.columns)}\n"
            data_context += f"Number of rows: {len(data)}\n"
            data_context += "Sample data summary:\n"
            data_context += str(data.describe().to_string())
            
            messages.append({
                "role": "system",
                "content": f"Current data context:\n{data_context}"
            })
        
        # Add context if provided
        if context:
            messages.append({
                "role": "system",
                "content": f"Additional context: {context}"
            })
            
        # Add conversation summary if history is long
        if len(self.conversation_history) > 3:
            messages.append({
                "role": "system",
                "content": self.summarize_conversation()
            })
        
        # Add recent conversation history
        for exchange in self.conversation_history[-3:]:  # Only include last 3 exchanges
            messages.extend([
                {"role": "user", "content": exchange["user"]},
                {"role": "assistant", "content": exchange["assistant"]}
            ])
            
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        return messages
            
    def generate_response(self, user_message: str, context: str = "", stream: bool = False, data: pd.DataFrame = None) -> Union[str, Generator[str, None, None]]:
        """Generate a response using the local server"""
        try:
            # Check if user requested a graph
            if "graph" in user_message.lower() and data is not None:
                generate_graph(data)
                return "I've generated a graph showing crop yield analysis. You can find it as 'crop_yield_analysis.png' in the current directory."
            
            # Get messages in OpenAI format with data context
            messages = self.get_messages(user_message, context, data)
            
            # Prepare the request payload
            payload = {
                "model": "llama-3.2-1b-instruct",  # Model identifier
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 300,
                "stream": stream
            }
            
            print(f"Sending request to {self.base_url}/v1/chat/completions")
            print(f"Request payload: {json.dumps(payload, indent=2)}")
            
            # Make request to local server with timeout
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
                stream=stream
            )
            
            print(f"Server response status: {response.status_code}")
            
            if response.status_code == 200:
                if stream:
                    return self._handle_streaming_response(response, user_message)
                else:
                    return self._handle_normal_response(response, user_message)
            else:
                print(f"Server error: {response.status_code}")
                print(f"Response content: {response.text}")
                return self.get_fallback_response(user_message)
                
        except requests.exceptions.ConnectionError:
            print("Could not connect to local server. Please check if the server is running.")
            return self.get_fallback_response(user_message)
        except requests.exceptions.Timeout:
            print("Request to server timed out. Please try again.")
            return self.get_fallback_response(user_message)
        except Exception as e:
            print(f"Error generating response: {e}")
            return self.get_fallback_response(user_message)

    def set_current_data(self, data: pd.DataFrame):
        """Set the current data for analysis"""
        self.current_data = data
            
    def _handle_streaming_response(self, response: requests.Response, user_message: str) -> Generator[str, None, None]:
        """Handle streaming response from server"""
        collected_messages = []
        
        for line in response.iter_lines():
            if line:
                try:
                    json_object = json.loads(line.decode('utf-8').split('data: ')[1])
                    content = json_object['choices'][0]['delta'].get('content', '')
                    if content:
                        collected_messages.append(content)
                        yield content
                except Exception as e:
                    print(f"Error parsing streaming response: {e}")
                    continue
        
        # Add complete response to history
        full_response = ''.join(collected_messages)
        if full_response:
            self.add_to_history(user_message, full_response)
            
    def _handle_normal_response(self, response: requests.Response, user_message: str) -> str:
        """Handle normal (non-streaming) response from server"""
        try:
            result = response.json()
            print(f"Parsed response: {json.dumps(result, indent=2)}")
            
            # Extract response text using OpenAI format
            response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            if not response_text:
                print("Warning: Empty response received from server")
                return self.get_fallback_response(user_message)
            
            # Add to conversation history
            self.add_to_history(user_message, response_text)
            
            return response_text
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response.text}")
            return self.get_fallback_response(user_message)
        
    def get_fallback_response(self, user_message: str) -> str:
        """Generate a fallback response when server request fails"""
        message = user_message.lower()
        
        if any(word in message for word in ['hello', 'hi', 'namaste']):
            return "Hello! I'm your agriculture data analysis assistant. How can I help you?"
            
        elif any(word in message for word in ['data', 'analysis']):
            return "I can help you analyze agricultural data. Would you like to know about any specific dataset or analysis?"
            
        elif any(word in message for word in ['help']):
            return "I can help you in the following ways:\n1. Data Analysis\n2. Data Visualization\n3. Statistical Information\n4. Agricultural Recommendations"
            
        else:
            return "I'm sorry, I didn't understand your question. Please ask again or type 'help'." 

def generate_graph(data, title="Crop Yield Analysis"):
    """
    Generate a graph based on the provided data.
    
    Args:
        data (pd.DataFrame): The data to visualize.
        title (str): The title of the graph.
    """
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Crop', y='Yield', data=data)
    plt.title(title)
    plt.xlabel('Crop')
    plt.ylabel('Yield')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('crop_yield_analysis.png')  # Save the graph as an image
    plt.close()

# Example usage
# Assuming 'data' is a DataFrame with columns 'Crop' and 'Yield'
# generate_graph(data) 