"""Gateway models - Pydantic models for request/response validation."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


# ---- Chat Completions Models ----

class ChatCompletionMessage(BaseModel):
    role: str
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatCompletionMessage]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[str, int]] = None
    user: Optional[str] = None
    response_format: Optional[Dict[str, Any]] = None
    seed: Optional[int] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    parallel_tool_calls: Optional[bool] = None
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Union[str, Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    store: Optional[bool] = None
    extra_body: Optional[Dict[str, Any]] = None


# ---- Response API Models ----

class ResponseRequest(BaseModel):
    model: str
    input: Union[str, List[Dict[str, Any]]]
    instructions: Optional[str] = None
    max_output_tokens: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    parallel_tool_calls: Optional[bool] = None
    previous_response_id: Optional[str] = None
    store: Optional[bool] = None
    stream: Optional[bool] = False
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    truncation: Optional[str] = None
    user: Optional[str] = None
    reasoning: Optional[Dict[str, Any]] = None
    text: Optional[Dict[str, Any]] = None
    include: Optional[List[str]] = None
    extra_body: Optional[Dict[str, Any]] = None
    background: Optional[bool] = None
    prompt: Optional[Dict[str, Any]] = None


# ---- Models API ----

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = "aisuite4cn"


class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]


# ---- Error Response ----

class ErrorResponse(BaseModel):
    error: Dict[str, Any]
