import os
import time
from typing import List, Optional, Dict, Any
import voyageai
from dotenv import load_dotenv

load_dotenv()


class VoyageAIClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "voyage-code-2"):
        self.api_key = api_key or os.getenv("VOYAGE_API_KEY")
        self.model = model
        self.client = None
        
        if not self.api_key:
            raise ValueError("VoyageAI API key not provided. Set VOYAGE_API_KEY environment variable or pass api_key parameter.")
    
    def _get_client(self) -> voyageai.Client:
        if self.client is None:
            self.client = voyageai.Client(api_key=self.api_key)
        return self.client
    
    def test_connection(self) -> Dict[str, Any]:
        try:
            start_time = time.time()
            
            test_text = "This is a test embedding for connection validation."
            result = self.embed([test_text])
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                "success": True,
                "latency_ms": round(latency, 2),
                "model": self.model,
                "embedding_dimensions": len(result.embeddings[0]) if result.embeddings else 0,
                "total_tokens": result.total_tokens if hasattr(result, 'total_tokens') else None,
                "message": "VoyageAI connection successful"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"VoyageAI connection failed: {str(e)}"
            }
    
    def embed(self, texts: List[str], input_type: str = "document") -> Any:
        client = self._get_client()
        return client.embed(
            texts=texts,
            model=self.model,
            input_type=input_type
        )
    
    def embed_single(self, text: str, input_type: str = "document") -> List[float]:
        result = self.embed([text], input_type=input_type)
        return result.embeddings[0]
    
    def get_model_info(self) -> Dict[str, str]:
        return {
            "model": self.model,
            "provider": "VoyageAI",
            "api_key_configured": bool(self.api_key)
        }