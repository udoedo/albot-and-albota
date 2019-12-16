import asyncio
import unittest


from cogs import memes
from tests.helpers import MockBot, MockContext

class MyTestCase(unittest.TestCase):
    def test_blue_command(self):
        """Test if the `!hello python` command correctly print hello world in python."""
        mocked_bot = MockBot()
        bot_cog = memes.Memes(mocked_bot)
        mocked_context = MockContext()

        text = "ORANGE!"
        asyncio.run(bot_cog.blue.callback(bot_cog, mocked_context))
        mocked_context.send.assert_called_with(text)

    def test_orange_command(self):
        """Test if the `!hello python` command correctly print hello world in python."""
        mocked_bot = MockBot()
        bot_cog = memes.Memes(mocked_bot)
        mocked_context = MockContext()

        text = "BLUE!"
        asyncio.run(bot_cog.orange.callback(bot_cog, mocked_context))
        mocked_context.send.assert_called_with(text)

    def test_command_with_user_input(self):
        """Test if the `!hello python` command correctly print hello world in python."""
        mocked_bot = MockBot()
        bot_cog = memes.Memes(mocked_bot)
        mocked_context = MockContext()

        text = "funguje"
        asyncio.run(bot_cog.say.callback(bot_cog, mocked_context, phrase="funguje"))
        mocked_context.send.assert_called_with(text)


    # def test_command_drink(self):
    #     test_values = (
    #         (True, 'Thanks for the drink ~uwu~\nYou should drink something too!'),
    #         (False, 'Sowwy I\'m not vewy thwisty umu'),
    #     )
    #
    #     for thirsty, expected_conversion in test_values:
    #         with self.subTest(thirsty=thirsty, expected_conversion=expected_conversion):
    #             mocked_bot = MockBot()
    #             bot_cog = memes.Memes(mocked_bot)
    #
    #             bot_cog.thirsty = thirsty
    #             bot_cog.drink = False
    #             bot_cog.hydration = 20
    #
    #             mocked_context = MockContext()
    #
    #             asyncio.run(bot_cog.drink(bot_cog, mocked_context))
    #             mocked_context.send.assert_called_with(expected_conversion)




if __name__ == '__main__':
    unittest.main()
