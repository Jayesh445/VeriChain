"""
Gemini API integration with async support, error handling, and retry logic.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger

from app.core.config import settings
from app.models import AgentConfig


class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors."""
    pass


class GeminiClient:
    """
    Async client for Google Gemini API with robust error handling and retry logic.
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[AgentConfig] = None):
        self.api_key = api_key or settings.effective_api_key
        if not self.api_key:
            raise GeminiAPIError("No API key provided. Set GEMINI_API_KEY or GOOGLE_API_KEY in environment.")
        self.config = config or AgentConfig()
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        # HTTP client configuration
        self.timeout = httpx.Timeout(
            connect=10.0,
            read=self.config.timeout_seconds,
            write=10.0,
            pool=10.0
        )
        
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _build_headers(self) -> Dict[str, str]:
        """Build headers for API requests."""
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
    
    def _build_request_payload(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Build the request payload for Gemini API."""
        contents = [{"parts": [{"text": prompt}]}]
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_tokens,
                "topP": 0.8,
                "topK": 10
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        
        return payload
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError, GeminiAPIError))
    )
    async def _make_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make async HTTP request to Gemini API with retry logic."""
        try:
            logger.info(f"Making request to Gemini API: {url}")
            
            response = await self.client.post(
                url=url,
                headers=self._build_headers(),
                json=payload
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 429:
                raise GeminiAPIError("Rate limit exceeded")
            elif e.response.status_code == 401:
                raise GeminiAPIError("Invalid API key")
            elif e.response.status_code >= 500:
                raise GeminiAPIError(f"Server error: {e.response.status_code}")
            else:
                raise GeminiAPIError(f"API error: {e.response.status_code}")
        
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise GeminiAPIError(f"Request failed: {str(e)}")
    
    def _extract_response_text(self, response: Dict[str, Any]) -> str:
        """Extract text from Gemini API response."""
        try:
            candidates = response.get("candidates", [])
            if not candidates:
                raise GeminiAPIError("No candidates in response")
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                raise GeminiAPIError("No parts in response")
            
            return parts[0].get("text", "").strip()
            
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting response text: {e}")
            raise GeminiAPIError("Invalid response format")
    
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> str:
        """
        Generate text using Gemini API.
        
        Args:
            prompt: The input prompt
            system_instruction: Optional system instruction
            model_name: Optional model name override
            
        Returns:
            Generated text response
        """
        model = model_name or self.config.model_name
        url = f"{self.base_url}/{model}:generateContent"
        
        payload = self._build_request_payload(prompt, system_instruction)
        
        logger.info(f"Generating text with model: {model}")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        start_time = datetime.utcnow()
        
        try:
            response = await self._make_request(url, payload)
            generated_text = self._extract_response_text(response)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Text generation completed in {processing_time:.2f}s")
            logger.debug(f"Response length: {len(generated_text)} characters")
            
            return generated_text
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Text generation failed after {processing_time:.2f}s: {str(e)}")
            raise
    
    async def generate_structured_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response using Gemini API.
        
        Args:
            prompt: The input prompt
            system_instruction: Optional system instruction
            response_schema: Optional JSON schema for response validation
            
        Returns:
            Parsed JSON response
        """
        # Add JSON formatting instruction to the prompt
        json_prompt = f"""
{prompt}

Please respond with a valid JSON object that follows this structure.
Ensure your response is valid JSON without any additional text or formatting.
"""
        
        if response_schema:
            json_prompt += f"\n\nExpected JSON schema:\n{json.dumps(response_schema, indent=2)}"
        
        # Add JSON instruction to system prompt
        json_system_instruction = "You are a helpful assistant that always responds with valid JSON."
        if system_instruction:
            json_system_instruction = f"{system_instruction}\n\n{json_system_instruction}"
        
        response_text = await self.generate_text(
            prompt=json_prompt,
            system_instruction=json_system_instruction
        )
        
        try:
            # Try to parse JSON response
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text}")
            
            # Try to extract JSON from response if it contains extra text
            try:
                # Look for JSON object in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_text = response_text[start_idx:end_idx]
                    return json.loads(json_text)
                else:
                    raise GeminiAPIError("No JSON object found in response")
                    
            except json.JSONDecodeError:
                raise GeminiAPIError(f"Invalid JSON response: {response_text[:200]}...")
    
    async def validate_api_key(self) -> bool:
        """
        Validate the API key by making a simple request.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            await self.generate_text("Hello", model_name="gemini-1.5-flash")
            return True
        except GeminiAPIError as e:
            if "Invalid API key" in str(e):
                return False
            # Other errors might be temporary, so we consider the key valid
            return True
        except Exception:
            # Network errors, etc. - assume key is valid
            return True
    
    async def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Model name to get info for
            
        Returns:
            Model information
        """
        model = model_name or self.config.model_name
        url = f"{self.base_url}/{model}"
        
        try:
            response = await self.client.get(
                url=url,
                headers=self._build_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise GeminiAPIError(f"Failed to get model info: {e.response.status_code}")
        except httpx.RequestError as e:
            raise GeminiAPIError(f"Request failed: {str(e)}")


# Utility functions
async def create_gemini_client(api_key: Optional[str] = None, config: Optional[AgentConfig] = None) -> GeminiClient:
    """
    Create a Gemini client with configuration.
    
    Args:
        api_key: Optional API key override
        config: Optional configuration override
        
    Returns:
        Configured GeminiClient instance
    """
    api_key = api_key or settings.GOOGLE_API_KEY
    if not api_key:
        raise ValueError("Google API key is required")
    
    return GeminiClient(api_key=api_key, config=config)


async def test_gemini_connection(api_key: Optional[str] = None) -> bool:
    """
    Test connection to Gemini API.
    
    Args:
        api_key: Optional API key to test
        
    Returns:
        True if connection is successful
    """
    try:
        async with await create_gemini_client(api_key) as client:
            return await client.validate_api_key()
    except Exception as e:
        logger.error(f"Gemini connection test failed: {e}")
        return False