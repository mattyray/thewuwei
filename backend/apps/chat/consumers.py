"""
WebSocket consumer for the chat interface.

Handles:
1. Authentication (reject anonymous connections)
2. Receiving user messages
3. Calling the LangGraph agent
4. Sending responses back to the client
5. Persisting chat history
"""

import asyncio
import logging
import os
import traceback

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import ChatMessage

logger = logging.getLogger(__name__)

AGENT_TIMEOUT = 120  # seconds


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            logger.warning("WS rejected: anonymous user")
            await self.close()
            return

        logger.info("WS connected: user=%s", self.user.email)
        await self.accept()

    async def disconnect(self, close_code):
        logger.info("WS disconnected: code=%s", close_code)

    async def receive_json(self, content):
        message_type = content.get("type")
        if message_type != "message":
            return

        user_content = content.get("content", "").strip()
        if not user_content:
            return

        logger.info("WS message from %s: %s", self.user.email, user_content[:100])

        # Save user message
        await self.save_message("user", user_content)

        try:
            # Get agent response with timeout
            response_text = await asyncio.wait_for(
                self.get_agent_response(user_content),
                timeout=AGENT_TIMEOUT,
            )

            # Save assistant message
            await self.save_message("assistant", response_text)

            logger.info("WS response to %s: %s", self.user.email, response_text[:100])

            # Send complete response
            await self.send_json({
                "type": "complete",
                "content": response_text,
            })
        except asyncio.TimeoutError:
            logger.error("Agent timed out after %ss for user %s", AGENT_TIMEOUT, self.user.email)
            await self.send_json({
                "type": "complete",
                "content": "Sorry, the request timed out. Please try again.",
            })
        except Exception as e:
            logger.error("Agent error for %s: %s\n%s", self.user.email, e, traceback.format_exc())
            await self.send_json({
                "type": "complete",
                "content": f"Sorry, something went wrong: {e}",
            })

    async def get_agent_response(self, user_message: str) -> str:
        """Call the LangGraph agent and return the response text.

        This method is designed to be easily mocked in tests.
        In production, it invokes the full agent graph.
        """
        result = await database_sync_to_async(self._run_agent)(user_message)
        return result

    def _run_agent(self, user_message: str) -> str:
        """Synchronous agent invocation (runs in thread via database_sync_to_async)."""
        from langchain_core.messages import HumanMessage

        from apps.agent.graph import agent

        # Use user's API key if set, otherwise fall back to env var
        api_key = self.user.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")

        config = {
            "configurable": {
                "user": self.user,
                "anthropic_api_key": api_key,
            }
        }

        logger.info("Invoking agent for %s (key=%s...)", self.user.email, api_key[:10] if api_key else "NONE")

        result = agent.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config,
        )

        # Extract the last AI message content
        last_message = result["messages"][-1]
        return last_message.content

    @database_sync_to_async
    def save_message(self, role: str, content: str):
        ChatMessage.objects.create(
            user=self.user,
            role=role,
            content=content,
        )
