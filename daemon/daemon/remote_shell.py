import asyncio
import logging as log
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
from daemon.shell import Shell

class RemoteShell:
    def __init__(self, shell: "Shell"):
        self.shell = shell

    async def enter(self, websocket_url: str):
        log.info("Connecting to remote shell at %s.", websocket_url)

        try:
            async with connect(websocket_url) as websocket:
                log.info("Connected to remote shell.")

                async def recv_input():
                    return await websocket.recv()

                async def send_output(data: str):
                    await websocket.send(data)

                self.shell.set_input_source(recv_input)
                self.shell.set_output_sink(send_output)

                await self.shell.enter()

        except ConnectionClosed:
            log.info("WebSocket connection closed by remote. Exiting shell.")
        except Exception as e:
            log.error(f"Error in remote shell: {e}")
        finally:
            await self.shell.exit()
            log.info("Exited remote shell session.")

