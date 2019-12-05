from __future__ import annotations

import asyncio
import collections
import functools
import inspect
import itertools
import logging
import unittest.mock
from typing import Any, Iterable, Optional

import discord
from discord.ext.commands import Bot, Context

for logger in logging.Logger.manager.loggerDict.values():
    # Set all loggers to CRITICAL by default to prevent screen clutter during testing

    if not isinstance(logger, logging.Logger):
        # There might be some logging.PlaceHolder objects in there
        continue

    logger.setLevel(logging.CRITICAL)


def async_test(wrapped):
    """
    Run a test case via asyncio.
    Example:
        >>> @async_test
        ... async def lemon_wins():
        ...     assert True
    """

    @functools.wraps(wrapped)
    def wrapper(*args, **kwargs):
        return asyncio.run(wrapped(*args, **kwargs))

    return wrapper


class HashableMixin(discord.mixins.EqualityComparable):
    """
    Mixin that provides similar hashing and equality functionality as discord.py's `Hashable` mixin.
    Note: discord.py`s `Hashable` mixin bit-shifts `self.id` (`>> 22`); to prevent hash-collisions
    for the relative small `id` integers we generally use in tests, this bit-shift is omitted.
    """

    def __hash__(self):
        return self.id


class ColourMixin:
    """A mixin for Mocks that provides the aliasing of color->colour like discord.py does."""

    @property
    def color(self) -> discord.Colour:
        return self.colour

    @color.setter
    def color(self, color: discord.Colour) -> None:
        self.colour = color


class CustomMockMixin:
    """
    Provides common functionality for our custom Mock types.
    The cooperative `__init__` automatically creates `AsyncMock` attributes for every coroutine
    function `inspect` detects in the `spec` instance we provide. In addition, this mixin takes care
    of making sure child mocks are instantiated with the correct class. By default, the mock of the
    children will be `unittest.mock.MagicMock`, but this can be overwritten by setting the attribute
    `child_mock_type` on the custom mock inheriting from this mixin.
    """

    child_mock_type = unittest.mock.MagicMock
    discord_id = itertools.count(0)

    def __init__(self, spec_set: Any = None, **kwargs):
        name = kwargs.pop('name', None)  # `name` has special meaning for Mock classes, so we need to set it manually.
        super().__init__(spec_set=spec_set, **kwargs)

        if name:
            self.name = name
        if spec_set:
            self._extract_coroutine_methods_from_spec_instance(spec_set)

    def _get_child_mock(self, **kw):
        """
        Overwrite of the `_get_child_mock` method to stop the propagation of our custom mock classes.
        Mock objects automatically create children when you access an attribute or call a method on them. By default,
        the class of these children is the type of the parent itself. However, this would mean that the children created
        for our custom mock types would also be instances of that custom mock type. This is not desirable, as attributes
        of, e.g., a `Bot` object are not `Bot` objects themselves. The Python docs for `unittest.mock` hint that
        overwriting this method is the best way to deal with that.
        This override will look for an attribute called `child_mock_type` and use that as the type of the child mock.
        """
        klass = self.child_mock_type

        if self._mock_sealed:
            attribute = "." + kw["name"] if "name" in kw else "()"
            mock_name = self._extract_mock_name() + attribute
            raise AttributeError(mock_name)

        return klass(**kw)

    def _extract_coroutine_methods_from_spec_instance(self, source: Any) -> None:
        """Automatically detect coroutine functions in `source` and set them as AsyncMock attributes."""
        for name, _method in inspect.getmembers(source, inspect.iscoroutinefunction):
            setattr(self, name, AsyncMock())


# TODO: Remove me in Python 3.8
class AsyncMock(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock async callables.
    Python 3.8 will introduce an AsyncMock class in the standard library that will have some more
    features; this stand-in only overwrites the `__call__` method to an async version.
    """

    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class AsyncIteratorMock:
    """
    A class to mock asynchronous iterators.
    This allows async for, which is used in certain Discord.py objects. For example,
    an async iterator is returned by the Reaction.users() method.
    """

    def __init__(self, iterable: Iterable = None):
        if iterable is None:
            iterable = []

        self.iter = iter(iterable)
        self.iterable = iterable

        self.call_count = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration

    def __call__(self):
        """
        Keeps track of the number of times an instance has been called.
        This is useful, since it typically shows that the iterator has actually been used somewhere after we have
        instantiated the mock for an attribute that normally returns an iterator when called.
        """
        self.call_count += 1
        return self

    @property
    def return_value(self):
        """Makes `self.iterable` accessible as self.return_value."""
        return self.iterable

    @return_value.setter
    def return_value(self, iterable):
        """Stores the `return_value` as `self.iterable` and its iterator as `self.iter`."""
        self.iter = iter(iterable)
        self.iterable = iterable

    def assert_called(self):
        """Asserts if the AsyncIteratorMock instance has been called at least once."""
        if self.call_count == 0:
            raise AssertionError("Expected AsyncIteratorMock to have been called.")

    def assert_called_once(self):
        """Asserts if the AsyncIteratorMock instance has been called exactly once."""
        if self.call_count != 1:
            raise AssertionError(
                f"Expected AsyncIteratorMock to have been called once. Called {self.call_count} times."
            )

    def assert_not_called(self):
        """Asserts if the AsyncIteratorMock instance has not been called."""
        if self.call_count != 0:
            raise AssertionError(
                f"Expected AsyncIteratorMock to not have been called once. Called {self.call_count} times."
            )

    def reset_mock(self):
        """Resets the call count, but not the return value or iterator."""
        self.call_count = 0


# Create a guild instance to get a realistic Mock of `discord.Guild`
guild_data = {
    'id': 1,
    'name': 'guild',
    'region': 'Europe',
    'verification_level': 2,
    'default_notications': 1,
    'afk_timeout': 100,
    'icon': "icon.png",
    'banner': 'banner.png',
    'mfa_level': 1,
    'splash': 'splash.png',
    'system_channel_id': 464033278631084042,
    'description': 'mocking is fun',
    'max_presences': 10_000,
    'max_members': 100_000,
    'preferred_locale': 'UTC',
    'owner_id': 1,
    'afk_channel_id': 464033278631084042,
}
guild_instance = discord.Guild(data=guild_data, state=unittest.mock.MagicMock())


class MockGuild(CustomMockMixin, unittest.mock.Mock, HashableMixin):
    """
    A `Mock` subclass to mock `discord.Guild` objects.
    A MockGuild instance will follow the specifications of a `discord.Guild` instance. This means
    that if the code you're testing tries to access an attribute or method that normally does not
    exist for a `discord.Guild` object this will raise an `AttributeError`. This is to make sure our
    tests fail if the code we're testing uses a `discord.Guild` object in the wrong way.
    One restriction of that is that if the code tries to access an attribute that normally does not
    exist for `discord.Guild` instance but was added dynamically, this will raise an exception with
    the mocked object. To get around that, you can set the non-standard attribute explicitly for the
    instance of `MockGuild`:
    >>> guild = MockGuild()
    >>> guild.attribute_that_normally_does_not_exist = unittest.mock.MagicMock()
    In addition to attribute simulation, mocked guild object will pass an `isinstance` check against
    `discord.Guild`:
    >>> guild = MockGuild()
    >>> isinstance(guild, discord.Guild)
    True
    For more info, see the `Mocking` section in `tests/README.md`.
    """

    def __init__(self, roles: Optional[Iterable[MockRole]] = None, **kwargs) -> None:
        default_kwargs = {'id': next(self.discord_id), 'members': []}
        super().__init__(spec_set=guild_instance, **collections.ChainMap(kwargs, default_kwargs))

        self.roles = [MockRole(name="@everyone", position=1, id=0)]
        if roles:
            self.roles.extend(roles)


# Create a Role instance to get a realistic Mock of `discord.Role`
role_data = {'name': 'role', 'id': 1}
role_instance = discord.Role(guild=guild_instance, state=unittest.mock.MagicMock(), data=role_data)


class MockRole(CustomMockMixin, unittest.mock.Mock, ColourMixin, HashableMixin):
    """
    A Mock subclass to mock `discord.Role` objects.
    Instances of this class will follow the specifications of `discord.Role` instances. For more
    information, see the `MockGuild` docstring.
    """

    def __init__(self, **kwargs) -> None:
        default_kwargs = {'id': next(self.discord_id), 'name': 'role', 'position': 1}
        super().__init__(spec_set=role_instance, **collections.ChainMap(kwargs, default_kwargs))

        if 'mention' not in kwargs:
            self.mention = f'&{self.name}'

    def __lt__(self, other):
        """Simplified position-based comparisons similar to those of `discord.Role`."""
        return self.position < other.position


# Create a Member instance to get a realistic Mock of `discord.Member`
member_data = {'user': 'lemon', 'roles': [1]}
state_mock = unittest.mock.MagicMock()
member_instance = discord.Member(data=member_data, guild=guild_instance, state=state_mock)


class MockMember(CustomMockMixin, unittest.mock.Mock, ColourMixin, HashableMixin):
    """
    A Mock subclass to mock Member objects.
    Instances of this class will follow the specifications of `discord.Member` instances. For more
    information, see the `MockGuild` docstring.
    """

    def __init__(self, roles: Optional[Iterable[MockRole]] = None, **kwargs) -> None:
        default_kwargs = {'name': 'member', 'id': next(self.discord_id), 'bot': False}
        super().__init__(spec_set=member_instance, **collections.ChainMap(kwargs, default_kwargs))

        self.roles = [MockRole(name="@everyone", position=1, id=0)]
        if roles:
            self.roles.extend(roles)

        if 'mention' not in kwargs:
            self.mention = f"@{self.name}"


# Create a User instance to get a realistic Mock of `discord.User`
user_instance = discord.User(data=unittest.mock.MagicMock(), state=unittest.mock.MagicMock())


class MockUser(CustomMockMixin, unittest.mock.Mock, ColourMixin, HashableMixin):
    """
    A Mock subclass to mock User objects.
    Instances of this class will follow the specifications of `discord.User` instances. For more
    information, see the `MockGuild` docstring.
    """

    def __init__(self, **kwargs) -> None:
        default_kwargs = {'name': 'user', 'id': next(self.discord_id), 'bot': False}
        super().__init__(spec_set=user_instance, **collections.ChainMap(kwargs, default_kwargs))

        if 'mention' not in kwargs:
            self.mention = f"@{self.name}"


# Create a Bot instance to get a realistic MagicMock of `discord.ext.commands.Bot`
bot_instance = Bot(command_prefix=unittest.mock.MagicMock())
bot_instance.http_session = None
bot_instance.api_client = None


class MockBot(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock Bot objects.
    Instances of this class will follow the specifications of `discord.ext.commands.Bot` instances.
    For more information, see the `MockGuild` docstring.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(spec_set=bot_instance, **kwargs)

        # self.wait_for is *not* a coroutine function, but returns a coroutine nonetheless and
        # and should therefore be awaited. (The documentation calls it a coroutine as well, which
        # is technically incorrect, since it's a regular def.)
        self.wait_for = AsyncMock()

        # Since calling `create_task` on our MockBot does not actually schedule the coroutine object
        # as a task in the asyncio loop, this `side_effect` calls `close()` on the coroutine object
        # to prevent "has not been awaited"-warnings.
        self.loop.create_task.side_effect = lambda coroutine: coroutine.close()


# Create a TextChannel instance to get a realistic MagicMock of `discord.TextChannel`
channel_data = {
    'id': 1,
    'type': 'TextChannel',
    'name': 'channel',
    'parent_id': 1234567890,
    'topic': 'topic',
    'position': 1,
    'nsfw': False,
    'last_message_id': 1,
}
state = unittest.mock.MagicMock()
guild = unittest.mock.MagicMock()
channel_instance = discord.TextChannel(state=state, guild=guild, data=channel_data)


class MockTextChannel(CustomMockMixin, unittest.mock.Mock, HashableMixin):
    """
    A MagicMock subclass to mock TextChannel objects.
    Instances of this class will follow the specifications of `discord.TextChannel` instances. For
    more information, see the `MockGuild` docstring.
    """

    def __init__(self, name: str = 'channel', channel_id: int = 1, **kwargs) -> None:
        default_kwargs = {'id': next(self.discord_id), 'name': 'channel', 'guild': MockGuild()}
        super().__init__(spec_set=channel_instance, **collections.ChainMap(kwargs, default_kwargs))

        if 'mention' not in kwargs:
            self.mention = f"#{self.name}"


# Create a Message instance to get a realistic MagicMock of `discord.Message`
message_data = {
    'id': 1,
    'webhook_id': 431341013479718912,
    'attachments': [],
    'embeds': [],
    'application': 'Python Discord',
    'activity': 'mocking',
    'channel': unittest.mock.MagicMock(),
    'edited_timestamp': '2019-10-14T15:33:48+00:00',
    'type': 'message',
    'pinned': False,
    'mention_everyone': False,
    'tts': None,
    'content': 'content',
    'nonce': None,
}
state = unittest.mock.MagicMock()
channel = unittest.mock.MagicMock()
message_instance = discord.Message(state=state, channel=channel, data=message_data)

# Create a Context instance to get a realistic MagicMock of `discord.ext.commands.Context`
context_instance = Context(message=unittest.mock.MagicMock(), prefix=unittest.mock.MagicMock())


class MockContext(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock Context objects.
    Instances of this class will follow the specifications of `discord.ext.commands.Context`
    instances. For more information, see the `MockGuild` docstring.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(spec_set=context_instance, **kwargs)
        self.bot = kwargs.get('bot', MockBot())
        self.guild = kwargs.get('guild', MockGuild())
        self.author = kwargs.get('author', MockMember())
        self.channel = kwargs.get('channel', MockTextChannel())


attachment_instance = discord.Attachment(data=unittest.mock.MagicMock(id=1), state=unittest.mock.MagicMock())


class MockAttachment(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock Attachment objects.
    Instances of this class will follow the specifications of `discord.Attachment` instances. For
    more information, see the `MockGuild` docstring.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(spec_set=attachment_instance, **kwargs)


class MockMessage(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock Message objects.
    Instances of this class will follow the specifications of `discord.Message` instances. For more
    information, see the `MockGuild` docstring.
    """

    def __init__(self, **kwargs) -> None:
        default_kwargs = {'attachments': []}
        super().__init__(spec_set=message_instance, **collections.ChainMap(kwargs, default_kwargs))
        self.author = kwargs.get('author', MockMember())
        self.channel = kwargs.get('channel', MockTextChannel())


emoji_data = {'require_colons': True, 'managed': True, 'id': 1, 'name': 'hyperlemon'}
emoji_instance = discord.Emoji(guild=MockGuild(), state=unittest.mock.MagicMock(), data=emoji_data)


class MockEmoji(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock Emoji objects.
    Instances of this class will follow the specifications of `discord.Emoji` instances. For more
    information, see the `MockGuild` docstring.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(spec_set=emoji_instance, **kwargs)
        self.guild = kwargs.get('guild', MockGuild())


partial_emoji_instance = discord.PartialEmoji(animated=False, name='guido')


class MockPartialEmoji(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock PartialEmoji objects.
    Instances of this class will follow the specifications of `discord.PartialEmoji` instances. For
    more information, see the `MockGuild` docstring.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(spec_set=partial_emoji_instance, **kwargs)


reaction_instance = discord.Reaction(message=MockMessage(), data={'me': True}, emoji=MockEmoji())


class MockReaction(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock Reaction objects.
    Instances of this class will follow the specifications of `discord.Reaction` instances. For
    more information, see the `MockGuild` docstring.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(spec_set=reaction_instance, **kwargs)
        self.emoji = kwargs.get('emoji', MockEmoji())
        self.message = kwargs.get('message', MockMessage())
        self.users = AsyncIteratorMock(kwargs.get('users', []))


webhook_instance = discord.Webhook(data=unittest.mock.MagicMock(), adapter=unittest.mock.MagicMock())


class MockAsyncWebhook(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock Webhook objects using an AsyncWebhookAdapter.
    Instances of this class will follow the specifications of `discord.Webhook` instances. For
    more information, see the `MockGuild` docstring.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(spec_set=webhook_instance, **kwargs)

        # Because Webhooks can also use a synchronous "WebhookAdapter", the methods are not defined
        # as coroutines. That's why we need to set the methods manually.
        self.send = AsyncMock()
        self.edit = AsyncMock()
        self.delete = AsyncMock()
        self.execute = AsyncMock()
