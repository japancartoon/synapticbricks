"""
SynapticBricks Configuration Manager
Easy setup for API keys and advanced features
"""
import os
import json
from pathlib import Path
from typing import Optional


class Config:
    """Simple configuration manager for SynapticBricks."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".synapticbricks"
        self.config_file = self.config_dir / "config.json"
        self._config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load config from file or environment variables."""
        config = {}
        
        # Try loading from file
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        
        # Override with environment variables (higher priority)
        if os.getenv('SYNAPTICBRICKS_API_KEY'):
            config['api_key'] = os.getenv('SYNAPTICBRICKS_API_KEY')
        
        if os.getenv('SYNAPTICBRICKS_MODEL'):
            config['model'] = os.getenv('SYNAPTICBRICKS_MODEL')
        
        return config
    
    def save_config(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            "api_key": api_key,
            "model": model,
            "version": "1.4.1"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self._config = config
        print(f"✅ Config saved to: {self.config_file}")
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from config."""
        return self._config.get('api_key')
    
    def get_model(self) -> str:
        """Get preferred model."""
        return self._config.get('model', 'gemini-2.5-flash')
    
    def is_configured(self) -> bool:
        """Check if AI features are configured."""
        return self.get_api_key() is not None
    
    def clear(self):
        """Clear configuration."""
        if self.config_file.exists():
            self.config_file.unlink()
        self._config = {}
        print("✅ Configuration cleared")


# Global config instance
_config = Config()


def configure(api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
    """
    Configure SynapticBricks for AI-powered features.
    
    Args:
        api_key: Your Gemini API key (get one at https://ai.google.dev/)
        model: Preferred AI model (default: gemini-2.5-flash)
    
    Example:
        >>> import synapticbricks
        >>> synapticbricks.configure(api_key="YOUR_API_KEY")
        ✅ Config saved to: /home/user/.synapticbricks/config.json
        ✅ AI healing enabled!
    """
    _config.save_config(api_key=api_key, model=model)
    
    if api_key:
        print("✅ AI healing enabled!")
        print("   All bricks can now self-heal using AI 🧠")
    else:
        print("⚠️  No API key provided - AI healing disabled")
        print("   Core features still work perfectly!")


def get_config() -> Config:
    """Get global config instance."""
    return _config


def is_ai_enabled() -> bool:
    """Check if AI features are enabled."""
    return _config.is_configured()
