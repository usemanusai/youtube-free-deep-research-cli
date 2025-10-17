import json

try:
    with open('youtube_chat_cli_main/Local RAG AI Agent.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("✓ JSON is valid!")
    print(f"Workflow name: {data['name']}")
    print(f"Total nodes: {len(data['nodes'])}")
    print(f"Active: {data.get('active', False)}")
    
    # Check for key nodes
    node_names = [node['name'] for node in data['nodes']]
    print(f"\nKey nodes present:")
    for key_node in ['AI Agent', 'Vector Store Tool', 'Qdrant Vector Store', 'Ollama Chat Model']:
        if key_node in node_names:
            print(f"  ✓ {key_node}")
        else:
            print(f"  ✗ {key_node} MISSING!")
    
    # Check AI Agent configuration
    ai_agent = next((node for node in data['nodes'] if node['name'] == 'AI Agent'), None)
    if ai_agent:
        params = ai_agent.get('parameters', {})
        if params.get('promptType'):
            print(f"\n✓ AI Agent has prompt configuration")
        else:
            print(f"\n✗ AI Agent missing prompt configuration")
    
    # Check Vector Store Tool
    vector_tool = next((node for node in data['nodes'] if node['name'] == 'Vector Store Tool'), None)
    if vector_tool:
        params = vector_tool.get('parameters', {})
        if params.get('description'):
            print(f"✓ Vector Store Tool has description")
        else:
            print(f"✗ Vector Store Tool missing description")
    
    print("\n✓ Workflow validation complete!")
    
except json.JSONDecodeError as e:
    print(f"✗ JSON validation failed: {e}")
except Exception as e:
    print(f"✗ Error: {e}")

