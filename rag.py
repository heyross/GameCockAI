import ollama
import json
from tools import TOOL_MAP

def query_swapbot(user_query: str, messages: list):
    """Handles a user query by deciding whether to use a tool or answer directly.

    This function orchestrates the agentic loop:
    1.  Ask the model to either answer the user or call a tool.
    2.  If the model calls a tool, execute it.
    3.  Send the tool's result back to the model to get a final answer.

    Args:
        user_query (str): The user's latest query.
        messages (list): The history of the conversation.

    Returns:
        str: The AI's final response to the user.
    """
    messages.append({'role': 'user', 'content': user_query})

    # First call to the model to get its decision
    response = ollama.chat(
        model='mistral',
        messages=messages,
        tools=[tool['schema'] for tool in TOOL_MAP.values()],
        tool_choice='auto'  # Let the model decide
    )
    messages.append(response['message'])

    # Check if the model decided to use a tool
    if not response['message'].get('tool_calls'):
        return response['message']['content']

    # The model decided to use a tool, so we execute it
    tool_calls = response['message']['tool_calls']
    for tool_call in tool_calls:
        tool_name = tool_call['function']['name']
        tool_args = tool_call['function']['arguments']
        
        if tool_name in TOOL_MAP:
            tool_function = TOOL_MAP[tool_name]['function']
            
            # Execute the tool and get the result
            try:
                tool_result = tool_function(**tool_args)
                
                # Append the tool's output to the conversation history
                messages.append({
                    'role': 'tool',
                    'content': tool_result,
                })
            except Exception as e:
                print(f"Error executing tool {tool_name}: {e}")
                messages.append({
                    'role': 'tool',
                    'content': f'Error: Could not execute tool {tool_name}. Reason: {e}',
                })

    # Second call to the model with the tool's output
    final_response = ollama.chat(
        model='mistral',
        messages=messages
    )
    messages.append(final_response['message'])
    return final_response['message']['content']
