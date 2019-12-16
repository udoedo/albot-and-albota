# import unittest
#
#
# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, True)
#
#     def
#
#
# if __name__ == '__main__':
#     unittest.main()
#
import asyncio
import unittest


from cogs import helloworld
from tests.helpers import MockBot, MockContext


class BotCogTests(unittest.TestCase):
    def test_command_with_python_as_input(self):
        """Test if the `!hello python` command correctly print hello world in python."""
        mocked_bot = MockBot()
        bot_cog = helloworld.HelloWorld(mocked_bot)
        mocked_context = MockContext()

        text = "```python\nprint(\"Hello, World!\")\n```\n"
        asyncio.run(bot_cog.hello.callback(bot_cog, mocked_context, lang="Python"))
        mocked_context.send.assert_called_with(text)

    def test_langs_command_listing_all_available_languages(self):
        """Test if the !hellolangs prints all the available languages"""
        mocked_bot = MockBot()
        bot_cog = helloworld.HelloWorld(mocked_bot)
        mocked_context = MockContext()

        text = "arm\nbash\nc\ncobol\ncpp\ncsharp\nerlang\ngo\nhaskell\njava\njavascript\njulia\nlisp\nlua\nobjectivec\npascal\nperl\nphp\npython\nruby\nrust\nscala\nswift\n"

        asyncio.run(bot_cog.hellolangs.callback(bot_cog, mocked_context))
        mocked_context.send.assert_called_with(text)

if __name__=="__main__":
    unittest.main()
