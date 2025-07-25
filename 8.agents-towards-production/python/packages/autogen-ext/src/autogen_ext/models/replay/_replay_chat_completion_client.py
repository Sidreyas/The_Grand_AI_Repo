from __future__ import annotations

import logging
import warnings
from typing import Any, AsyncGenerator, Dict, List, Literal, Mapping, Optional, Sequence, Union

from autogen_core import EVENT_LOGGER_NAME, CancellationToken, Component
from autogen_core.models import (
    ChatCompletionClient,
    CreateResult,
    LLMMessage,
    ModelCapabilities,  # type: ignore
    ModelFamily,
    ModelInfo,
    RequestUsage,
    validate_model_info,
)
from autogen_core.tools import Tool, ToolSchema
from pydantic import BaseModel
from typing_extensions import Self

logger = logging.getLogger(EVENT_LOGGER_NAME)


class ReplayChatCompletionClientConfig(BaseModel):
    """ReplayChatCompletionClient configuration."""

    chat_completions: Sequence[Union[str, CreateResult]]
    model_info: Optional[ModelInfo] = None


class ReplayChatCompletionClient(ChatCompletionClient, Component[ReplayChatCompletionClientConfig]):
    """
    A mock chat completion client that replays predefined responses using an index-based approach.

    This class simulates a chat completion client by replaying a predefined list of responses. It supports both single completion and streaming responses. The responses can be either strings or CreateResult objects. The client now uses an index-based approach to access the responses, allowing for resetting the state.

    .. note::
        The responses can be either strings or CreateResult objects.

    Args:
        chat_completions (Sequence[Union[str, CreateResult]]): A list of predefined responses to replay.

    Raises:
        ValueError("No more mock responses available"): If the list of provided outputs are exhausted.

    Examples:

    Simple chat completion client to return pre-defined responses.

        .. code-block:: python

            from autogen_core.models import UserMessage
            from autogen_ext.models.replay import ReplayChatCompletionClient


            async def example():
                chat_completions = [
                    "Hello, how can I assist you today?",
                    "I'm happy to help with any questions you have.",
                    "Is there anything else I can assist you with?",
                ]
                client = ReplayChatCompletionClient(chat_completions)
                messages = [UserMessage(content="What can you do?", source="user")]
                response = await client.create(messages)
                print(response.content)  # Output: "Hello, how can I assist you today?"

    Simple streaming chat completion client to return pre-defined responses

        .. code-block:: python

            import asyncio
            from autogen_core.models import UserMessage
            from autogen_ext.models.replay import ReplayChatCompletionClient


            async def example():
                chat_completions = [
                    "Hello, how can I assist you today?",
                    "I'm happy to help with any questions you have.",
                    "Is there anything else I can assist you with?",
                ]
                client = ReplayChatCompletionClient(chat_completions)
                messages = [UserMessage(content="What can you do?", source="user")]

                async for token in client.create_stream(messages):
                    print(token, end="")  # Output: "Hello, how can I assist you today?"

                async for token in client.create_stream(messages):
                    print(token, end="")  # Output: "I'm happy to help with any questions you have."

                asyncio.run(example())

    Using `.reset` to reset the chat client state

        .. code-block:: python

            import asyncio
            from autogen_core.models import UserMessage
            from autogen_ext.models.replay import ReplayChatCompletionClient


            async def example():
                chat_completions = [
                    "Hello, how can I assist you today?",
                ]
                client = ReplayChatCompletionClient(chat_completions)
                messages = [UserMessage(content="What can you do?", source="user")]
                response = await client.create(messages)
                print(response.content)  # Output: "Hello, how can I assist you today?"

                response = await client.create(messages)  # Raises ValueError("No more mock responses available")

                client.reset()  # Reset the client state (current index of message and token usages)
                response = await client.create(messages)
                print(response.content)  # Output: "Hello, how can I assist you today?" again


            asyncio.run(example())

    """

    __protocol__: ChatCompletionClient
    component_type = "replay_chat_completion_client"
    component_provider_override = "autogen_ext.models.replay.ReplayChatCompletionClient"
    component_config_schema = ReplayChatCompletionClientConfig

    # TODO: Support logprobs in Responses

    def __init__(
        self,
        chat_completions: Sequence[Union[str, CreateResult]],
        model_info: Optional[ModelInfo] = None,
    ):
        self.chat_completions = list(chat_completions)
        self.provided_message_count = len(self.chat_completions)
        if model_info is not None:
            self._model_info = model_info
            validate_model_info(self._model_info)
        else:
            self._model_info = ModelInfo(
                vision=False,
                function_calling=False,
                json_output=False,
                family=ModelFamily.UNKNOWN,
                structured_output=False,
            )
        self._total_available_tokens = 10000
        self._cur_usage = RequestUsage(prompt_tokens=0, completion_tokens=0)
        self._total_usage = RequestUsage(prompt_tokens=0, completion_tokens=0)
        self._current_index = 0
        self._cached_bool_value = True
        self._create_calls: List[Dict[str, Any]] = []

    @property
    def create_calls(self) -> List[Dict[str, Any]]:
        """Return the arguments of the calls made to the create method."""
        return self._create_calls

    async def create(
        self,
        messages: Sequence[LLMMessage],
        *,
        tools: Sequence[Tool | ToolSchema] = [],
        tool_choice: Tool | Literal["auto", "required", "none"] = "auto",
        json_output: Optional[bool | type[BaseModel]] = None,
        extra_create_args: Mapping[str, Any] = {},
        cancellation_token: Optional[CancellationToken] = None,
    ) -> CreateResult:
        """Return the next completion from the list."""
        # Warn if tool_choice is specified since it's ignored in replay mode
        if tool_choice != "auto":
            logger.warning("tool_choice parameter specified but is ignored in replay mode")

        if self._current_index >= len(self.chat_completions):
            raise ValueError("No more mock responses available")

        response = self.chat_completions[self._current_index]
        _, prompt_token_count = self._tokenize(messages)
        if isinstance(response, str):
            _, output_token_count = self._tokenize(response)
            self._cur_usage = RequestUsage(prompt_tokens=prompt_token_count, completion_tokens=output_token_count)
            response = CreateResult(
                finish_reason="stop", content=response, usage=self._cur_usage, cached=self._cached_bool_value
            )
        else:
            self._cur_usage = RequestUsage(
                prompt_tokens=prompt_token_count, completion_tokens=response.usage.completion_tokens
            )

        self._update_total_usage()
        self._current_index += 1
        self._create_calls.append(
            {
                "messages": messages,
                "tools": tools,
                "json_output": json_output,
                "extra_create_args": extra_create_args,
                "cancellation_token": cancellation_token,
            }
        )
        return response

    async def create_stream(
        self,
        messages: Sequence[LLMMessage],
        *,
        tools: Sequence[Tool | ToolSchema] = [],
        tool_choice: Tool | Literal["auto", "required", "none"] = "auto",
        json_output: Optional[bool | type[BaseModel]] = None,
        extra_create_args: Mapping[str, Any] = {},
        cancellation_token: Optional[CancellationToken] = None,
    ) -> AsyncGenerator[Union[str, CreateResult], None]:
        """Return the next completion as a stream."""
        # Warn if tool_choice is specified since it's ignored in replay mode
        if tool_choice != "auto":
            logger.warning("tool_choice parameter specified but is ignored in replay mode")

        if self._current_index >= len(self.chat_completions):
            raise ValueError("No more mock responses available")

        response = self.chat_completions[self._current_index]
        _, prompt_token_count = self._tokenize(messages)
        if isinstance(response, str):
            output_tokens, output_token_count = self._tokenize(response)
            self._cur_usage = RequestUsage(prompt_tokens=prompt_token_count, completion_tokens=output_token_count)

            for i, token in enumerate(output_tokens):
                if i < len(output_tokens) - 1:
                    yield token + " "
                else:
                    yield token
            yield CreateResult(
                finish_reason="stop", content=response, usage=self._cur_usage, cached=self._cached_bool_value
            )
            self._update_total_usage()
        else:
            self._cur_usage = RequestUsage(
                prompt_tokens=prompt_token_count, completion_tokens=response.usage.completion_tokens
            )
            yield response
            self._update_total_usage()

        self._current_index += 1

    async def close(self) -> None:
        pass

    def actual_usage(self) -> RequestUsage:
        return self._cur_usage

    def total_usage(self) -> RequestUsage:
        return self._total_usage

    def count_tokens(self, messages: Sequence[LLMMessage], *, tools: Sequence[Tool | ToolSchema] = []) -> int:
        _, token_count = self._tokenize(messages)
        return token_count

    def remaining_tokens(self, messages: Sequence[LLMMessage], *, tools: Sequence[Tool | ToolSchema] = []) -> int:
        return max(
            0, self._total_available_tokens - self._total_usage.prompt_tokens - self._total_usage.completion_tokens
        )

    def set_cached_bool_value(self, value: bool) -> None:
        self._cached_bool_value = value

    def _tokenize(self, messages: Union[str, LLMMessage, Sequence[LLMMessage]]) -> tuple[list[str], int]:
        total_tokens = 0
        all_tokens: List[str] = []
        if isinstance(messages, str):
            tokens = messages.split()
            total_tokens += len(tokens)
            all_tokens.extend(tokens)
        elif hasattr(messages, "content"):
            if isinstance(messages.content, str):  # type: ignore [reportAttributeAccessIssue]
                tokens = messages.content.split()  # type: ignore [reportAttributeAccessIssue]
                total_tokens += len(tokens)
                all_tokens.extend(tokens)
            else:
                logger.warning("Token count has been done only on string content")
        elif isinstance(messages, Sequence):
            for message in messages:
                if isinstance(message.content, str):  # type: ignore [reportAttributeAccessIssue, union-attr]
                    tokens = message.content.split()  # type: ignore [reportAttributeAccessIssue, union-attr]
                    total_tokens += len(tokens)
                    all_tokens.extend(tokens)
                else:
                    logger.warning("Token count has been done only on string content")
        return all_tokens, total_tokens

    def _update_total_usage(self) -> None:
        self._total_usage.completion_tokens += self._cur_usage.completion_tokens
        self._total_usage.prompt_tokens += self._cur_usage.prompt_tokens

    @property
    def capabilities(self) -> ModelCapabilities:  # type: ignore
        """Return mock capabilities."""
        warnings.warn("capabilities is deprecated, use model_info instead", DeprecationWarning, stacklevel=2)
        return self._model_info

    @property
    def model_info(self) -> ModelInfo:
        return self._model_info

    def reset(self) -> None:
        """Reset the client state and usage to its initial state."""
        self._cur_usage = RequestUsage(prompt_tokens=0, completion_tokens=0)
        self._total_usage = RequestUsage(prompt_tokens=0, completion_tokens=0)
        self._current_index = 0

    def _to_config(self) -> ReplayChatCompletionClientConfig:
        return ReplayChatCompletionClientConfig(
            chat_completions=self.chat_completions,
            model_info=self._model_info,
        )

    @classmethod
    def _from_config(cls, config: ReplayChatCompletionClientConfig) -> Self:
        return cls(
            chat_completions=config.chat_completions,
            model_info=config.model_info,
        )
