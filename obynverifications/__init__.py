from .config import get_config_categories, get_config_data
from .tasks import setup_tasks
from .verify import VerificationCog, ActionButton, VerifyButton
from .models import VerificationGuild, VerificationApp
from .api import module_api_bp

class Plugin:
    def __init__(self, bot):
        self.bot = bot

    async def enable_plugin(self):
        """Enable the plugin."""
        self.bot.add_cog(VerificationCog(self.bot))
        if self.bot.scheduler:
            setup_tasks(self.bot.scheduler)
        self.bot.add_view(VerifyButton())
        self.bot.add_view(ActionButton())
        print(f"Plugin '{__name__}' enabled successfully.")