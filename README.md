# Agriculture Data Analysis Chatbot

An AI-powered chatbot that helps farmers make informed decisions about crop selection and agricultural practices using real-time data analysis.

## Features

- **AI-Powered Chat Interface**: Uses LLM (Large Language Model) for natural conversation
- **Data Analysis**: Processes agricultural data to provide insights
- **Graph Generation**: Creates visual representations of crop yield data
- **Location-Based Recommendations**: Suggests suitable crops based on location data
- **Real-Time Data Processing**: Uses data from Kaggle for accurate analysis

## Technical Details

- **Backend**: Local server setup with LLM integration
- **LLM Model**: llama-3.2-1b-instruct
- **Server URL**: *you llm link from lm studio*
- **Data Source**: Kaggle datasets
- **Visualization**: Matplotlib and Seaborn for graph generation

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/AgricultureDataFresher.git
cd AgricultureDataFresher
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up the LLM server:

- Download and install the LLM model
- Configure the server URL in `llm_handler.py`

## Usage

1. Start the application:

```bash
python run.py
```

2. Interact with the chatbot:

- Ask questions about crop selection
- Request data analysis
- Generate graphs by including "graph" in your message

## Project Structure

```
AgricultureDataFresher/
├── llm_handler.py         # LLM integration and response handling
├── data_fresher.py        # Data processing and analysis
├── chat_interface.py      # Chat interface implementation
├── enhanced_chat_interface.py  # Advanced chat features
├── main.py                # Main application logic
├── run.py                 # Application entry point
└── requirements.txt       # Project dependencies
```

## Dependencies

- Python 3.x
- pandas
- matplotlib
- seaborn
- requests
- urllib3

## Acknowledgments

- Kaggle for providing agricultural datasets
- LM Studio for LLM integration
- Open-source community for various libraries and tools
