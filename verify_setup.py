#!/usr/bin/env python3
"""
Simple verification script to test the project structure and imports.
Run this to verify the implementation is working correctly.
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        from src.config import config
        print("✅ Configuration module imported successfully")
        
        # Test configuration validation
        validation = config.validate_config()
        print(f"✅ Configuration validation: {len(validation['issues'])} issues, {len(validation['warnings'])} warnings")
        
    except Exception as e:
        print(f"❌ Configuration module import failed: {e}")
        return False
    
    try:
        from src.voyageai_client import VoyageAIClient
        print("✅ VoyageAI client module imported successfully")
        
        # Test client initialization (without API key)
        try:
            client = VoyageAIClient(api_key="test-key")
            print("✅ VoyageAI client can be instantiated")
        except Exception as e:
            print(f"⚠️  VoyageAI client instantiation: {e}")
        
    except Exception as e:
        print(f"❌ VoyageAI client module import failed: {e}")
        return False
    
    try:
        from src.mongodb_client import MongoDBClient
        print("✅ MongoDB client module imported successfully")
        
        # Test client initialization
        client = MongoDBClient()
        print("✅ MongoDB client can be instantiated")
        
    except Exception as e:
        print(f"❌ MongoDB client module import failed: {e}")
        return False
    
    try:
        from src.commands.test_connection import test_connection_command
        print("✅ Test connection command imported successfully")
        
    except Exception as e:
        print(f"❌ Test connection command import failed: {e}")
        return False
    
    return True


def test_project_structure():
    """Test that all required files and directories exist."""
    print("\nTesting project structure...")
    
    required_files = [
        "main.py",
        "pyproject.toml",
        ".env.dist",
        "config.json.example",
        "src/__init__.py",
        "src/config.py",
        "src/voyageai_client.py",
        "src/mongodb_client.py",
        "src/commands/__init__.py",
        "src/commands/test_connection.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    print("\n✅ All required files exist")
    return True


def test_configuration():
    """Test configuration management."""
    print("\nTesting configuration...")
    
    try:
        from src.config import config
        
        # Test default configuration
        voyage_config = config.get_voyageai_config()
        mongodb_config = config.get_mongodb_config()
        
        print(f"✅ VoyageAI config keys: {list(voyage_config.keys())}")
        print(f"✅ MongoDB config keys: {list(mongodb_config.keys())}")
        
        # Test configuration validation
        validation = config.validate_config()
        print(f"✅ Configuration validation completed")
        
        if validation["issues"]:
            print("⚠️  Configuration issues found:")
            for issue in validation["issues"]:
                print(f"   - {issue}")
        
        if validation["warnings"]:
            print("⚠️  Configuration warnings:")
            for warning in validation["warnings"]:
                print(f"   - {warning}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("🔧 Verifying Spec-Kit CLI Implementation\n")
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Module Imports", test_imports),
        ("Configuration", test_configuration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} Test")
        print('='*50)
        
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*50}")
    print("VERIFICATION SUMMARY")
    print('='*50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All verification tests passed!")
        print("To complete setup:")
        print("1. Install dependencies: uv sync (or pip install -e .)")
        print("2. Copy .env.dist to .env and add your API keys")
        print("3. Run: python main.py test-connection")
    else:
        print("\n❌ Some verification tests failed.")
        print("Please check the errors above and fix any issues.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())