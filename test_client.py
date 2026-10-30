import asyncio
import json
import uuid

import websockets


async def main():

    uri = "ws://127.0.0.1:8765"

    async with websockets.connect(uri) as websocket:

        message = {
            "type": "chat.message",
            "id": str(uuid.uuid4()),
            "content": "summarize my emails and tell me what needs my attention",
        }

        await websocket.send(
            json.dumps(message)
        )

        async for raw_message in websocket:

            message = json.loads(raw_message)

            print(message)

            if message["type"] == "chat.chunk":
                print(
                    message["content"],
                    end="",
                    flush=True,
                )

            elif message["type"] == "chat.end":
                print()
                break

            elif message["type"] == "chat.error":
                print(
                    "\nERROR:",
                    message["error"],
                )
                break


if __name__ == "__main__":
    asyncio.run(main())