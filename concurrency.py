from openai import OpenAI
import os
import time
import threading
from dotenv import load_dotenv
# from termcolor import colored  # Uncomment if you wish to use colored output

# Load environment variables
load_dotenv()

# Retrieve the env variables
model = os.getenv('MODEL')
api_endpoint = os.getenv('API_ENDPOINT')

openai_api_base = api_endpoint + '/v1'

# FYI, a runpod api key only needs to be set if using serverless.
api_key = os.getenv('API_KEY') if os.getenv('API_KEY') is not None else "EMPTY"

# Initialize the OpenAI client
client = OpenAI(
    api_key=api_key,  # Replace with your actual API key if required
    base_url=openai_api_base,
)

def chat_completion_request_openai(messages, client, request_number):
    start_time = time.time()  # Start timing

    # Create chat completions using the OpenAI client
    chat_response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=200
    )

    print(chat_response)

    response_time = time.time() - start_time  # Calculate response time

    # Extract the completion text from the response
    if chat_response.choices:
        completion_text = chat_response.choices[0].message.content
    else:
        completion_text = None

    # Calculate tokens per second
    prompt_tokens = chat_response.usage.prompt_tokens if completion_text else 0
    tokens_generated = chat_response.usage.completion_tokens if completion_text else 0
    tokens_per_second = tokens_generated / response_time if response_time > 0 else 0

    # Print header and response details
    print(f"\n---------- Request #{request_number} ----------")
    print(f"Total Time Taken: {response_time:.2f} seconds")
    print(f"Prompt tokens: {prompt_tokens:.2f}")
    print(f"Tokens generated: {tokens_generated:.2f}")
    print(f"Tokens per Second: {tokens_per_second:.2f}\n")

    return completion_text

def send_request_every_x_seconds():
    for i in range(128):
        threading.Timer(0.06125 * i, send_request, args=(i+1,)).start()

def send_request(request_number):
    messages = [
        {"role": "user", "content": "Write a long essay on the topic of spring."}
    ]

    chat_completion_request_openai(messages, client, request_number)

# Start sending requests every x seconds
send_request_every_x_seconds()
