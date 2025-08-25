#!/usr/bin/env python3
"""
Simple test script to verify imports and basic functionality
"""

def test_imports():
    """Test all the key imports"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import os
        import tempfile
        print("✅ Basic imports OK")
        
        # Test Google GenAI
        from google import genai
        print("✅ Google GenAI import OK")
        
        # Test LangChain imports
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        print("✅ LangChain Google GenAI import OK")
        
        # Test our model module
        from model import get_model, get_langchain_embedding_engine
        print("✅ Model module import OK")
        
        # Test tools module
        from tools import create_tools_with_api_keys
        print("✅ Tools module import OK")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        return False


def test_embedding_creation():
    """Test creating an embedding engine"""
    try:
        print("\nTesting embedding engine creation...")
        
        # Test with a dummy API key
        from model import get_langchain_embedding_engine
        engine = get_langchain_embedding_engine("dummy_key")
        print("✅ Embedding engine creation OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding engine test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Draft 'n' Pray imports and basic functionality...\n")
    
    imports_ok = test_imports()
    if imports_ok:
        embedding_ok = test_embedding_creation()
        if embedding_ok:
            print("\n🎉 All tests passed! The app should work correctly.")
        else:
            print("\n⚠️  Embedding engine test failed. Check your Google GenAI setup.")
    else:
        print("\n❌ Import tests failed. Check your dependencies.")
