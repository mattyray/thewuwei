"""
WebSocket consumer for the chat interface.

Handles:
1. Authentication (reject anonymous connections)
2. Receiving user messages
3. Calling the LangGraph agent
4. Sending responses back to the client
5. Persisting chat history
"""

import json
import logging
import traceback

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import ChatMessage

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive_json(self, content):
        message_type = content.get("type")
        if message_type != "message":
            return

        user_content = content.get("content", "").strip()
        if not user_content:
            return

        # Save user message
        await self.save_message("user", user_content)

        try:
            # Get agent response
            response_text = await self.get_agent_response(user_content)

            # Save assistant message
            await self.save_message("assistant", response_text)

            # Send complete response
            await self.send_json({
                "type": "complete",
                "content": response_text,
            })
        except Exception as e:
            logger.error("Agent error: %s\n%s", e, traceback.format_exc())
            await self.send_json({
                "type": "complete",
                "content": f"Sorry, something went wrong: {e}",
            })

    async def get_agent_response(self, user_message: str) -> str:
        """Call the LangGraph agent and return the response text.

        This method is designed to be easily mocked in tests.
        In production, it invokes the full agent graph.
        """
        from apps.agent.graph import agent

        result = await database_sync_to_async(self._run_agent)(user_message)
        return result

    def _run_agent(self, user_message: str) -> str:
        """Synchronous agent invocation (runs in thread via database_sync_to_async)."""
        from langchain_core.messages import HumanMessage

        from apps.agent.graph import agent

        config = {
            "configurable": {
                "user": self.user,
                "anthropic_api_key": self.user.anthropic_api_key or None,
            }
        }

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
