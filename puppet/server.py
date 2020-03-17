import asyncio

from .state import ConversationState

class BotSessionContainer:
    def __init__(self, bot_coro, async_output_callback=None):
        self.responses = []
        self.s = ConversationState(async_output_callback or self.add_response)
        self.bot_task = asyncio.create_task(bot_coro(self.s))

    async def add_response(self, text):
        self.responses.append(text)

    def collect_responses(self):
        response = " ".join(self.responses)
        self.responses = []
        return response

class PuppetSessionsManager:
    def __init__(self, async_output_callback=None):
        self.sessions = {}
        self.async_output_callback = async_output_callback

    def session_cleanup_builder(self, bot, session_id):
        async def bot_coro(s):
            res = await bot(s)
            self.sessions.pop(session_id)
            return res
        return bot_coro

    def get_session(self, session_id, bot) -> BotSessionContainer:
        sc = self.sessions.get(session_id)
        if not sc:
            sc = BotSessionContainer(self.session_cleanup_builder(bot, session_id))
            self.sessions[session_id] = sc
        return sc