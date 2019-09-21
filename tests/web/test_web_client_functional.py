# Standard Imports
import unittest

# ThirdParty Imports
import asyncio
from aiohttp import web

# Internal Imports
import slack
from tests.helpers import async_test


class TestWebClientFunctional(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        task = asyncio.ensure_future(self.mock_server(), loop=self.loop)
        self.loop.run_until_complete(asyncio.wait_for(task, 0.1))
        self.client = slack.WebClient(
            token="xoxb-abc-123", base_url="http://localhost:8765", loop=self.loop
        )

    def tearDown(self):
        self.loop.run_until_complete(self.site.stop())

    async def mock_server(self):
        app = web.Application()
        app.router.add_post("/api.test", self.handler)
        runner = web.AppRunner(app)
        await runner.setup()
        self.site = web.TCPSite(runner, "localhost", 8765)
        await self.site.start()

    async def handler(self, request):
        assert request.content_type == "application/json"
        return web.json_response({"ok": True})

    @async_test
    async def test_requests_with_use_session_turned_off(self):
        self.client.use_pooling = False
        resp = await self.client.api_test()
        assert resp["ok"]

    @async_test
    async def test_subsequent_requests_with_a_session_succeeds(self):
        resp = await self.client.api_test()
        assert resp["ok"]
        resp = await self.client.api_test()
        assert resp["ok"]
