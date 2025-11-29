"""
Test Azure OpenAI integration for Day 8 Game Master agent
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_azure_env_vars():
    """Test that all required Azure environment variables are set"""
    load_dotenv(".env.local", override=True)
    
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    assert azure_endpoint, "AZURE_OPENAI_ENDPOINT not set"
    assert azure_key, "AZURE_OPENAI_API_KEY not set"
    assert azure_deployment, "AZURE_OPENAI_DEPLOYMENT not set"
    assert azure_version, "AZURE_OPENAI_API_VERSION not set"
    
    print("✓ All Azure environment variables present")
    print(f"  Endpoint: {azure_endpoint}")
    print(f"  Deployment: {azure_deployment}")
    print(f"  API Version: {azure_version}")

def test_openai_import():
    """Test that openai plugin is available"""
    try:
        from livekit.plugins import openai
        print("✓ openai plugin imported successfully")
        
        # Check for with_azure method
        assert hasattr(openai.LLM, 'with_azure'), "openai.LLM.with_azure method not found"
        print("✓ openai.LLM.with_azure method available")
    except ImportError as e:
        print(f"✗ Failed to import openai plugin: {e}")
        raise

def test_azure_llm_initialization():
    """Test that Azure LLM can be initialized with with_azure method"""
    load_dotenv(".env.local", override=True)
    
    from livekit.plugins import openai
    
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    try:
        llm = openai.LLM.with_azure(
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
            api_version=azure_version,
            api_key=azure_key,
        )
        print("✓ Azure LLM initialized successfully with with_azure() method")
        print(f"  LLM type: {type(llm)}")
    except Exception as e:
        print(f"✗ Failed to initialize Azure LLM: {e}")
        raise

def test_agent_instantiation():
    """Test that the Game Master agent can be instantiated"""
    load_dotenv(".env.local", override=True)
    
    from agent import GameMaster
    
    try:
        game_master = GameMaster(room_id="test_room", universe_preference="romance_drama")
        print("✓ Game Master agent instantiated successfully")
        print(f"  Room ID: {game_master.room_id}")
        print(f"  Universe preference: {game_master.universe_preference}")
    except Exception as e:
        print(f"✗ Failed to instantiate Game Master: {e}")
        raise

if __name__ == "__main__":
    print("Testing Azure OpenAI Integration for Day 8 Game Master Agent\n")
    
    try:
        test_azure_env_vars()
        print()
        test_openai_import()
        print()
        test_azure_llm_initialization()
        print()
        test_agent_instantiation()
        print("\n✓ All tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
