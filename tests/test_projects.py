# import unittest
# import asyncio
# from cogs import projects
# from tests.helpers import MockBot, MockContext, MockMember, MockRole, AsyncMock
#
#
# class MyTestProjects(unittest.TestCase):
#     # def test_leave_role(self):
#     #     '''testujeme nieco'''
#     #
#     #     member_data = {'user': 'lemon', 'roles': [
#     #         MockRole(name="muddy-swamp", position=2, id=1),
#     #         MockRole(name="club-website", position=3, id=2)
#     #     ]}
#     #     state_mock = unittest.mock.MagicMock()
#     #     member_instance = MockMember(member_data)
#     #     # user = MockMember()
#     #
#     #
#     #
#     #     # user = MockMember(name="johny", roles=[)
#     #     mocked_ctx = MockContext(author=member_instance)
#     #
#     #     test_user = MockMember(name="johny",roles="club-website")
#     #
#     #     # test_roles = MockRole(name="muddy-swamp",position=1, id=2)
#     #
#     #     asyncio.run(bot_cog.leave_role(bot_cog, mocked_ctx, role=('muddy-swamp')))
#     #
#     #     self.assertEqual(mocked_ctx.author.roles, test_user.roles)
#
#     def test_leave_commandik(self):
#         '''daco daco daco'''
#         mocked_bot = MockBot()
#         bot_cog = projects.Projects(mocked_bot)
#
#         bot_role = MockRole(name="bot-dev", id=1)
#         muddy_role = MockRole(name="muddy-swamp", id=2)
#
#         test_user = MockMember(name="Jimmy", roles=[bot_role,muddy_role])
#         expected_test_user = MockMember(roles=[muddy_role])
#         expected_role = "muddy-swamp"
#         mock_ctx = MockContext(author=test_user)
#
#         # print(mock_ctx.author.name)
#         # for role in mock_ctx.author.roles:
#         #     print(role.name)
#
#         # self.bot_cog.leave_role.callback(mock_ctx, role=["bot-dev","muddy-swamp"])
#         # as bot_cog.leave_role(mock_ctx,role=bot_role.name)
#         asyncio.run(bot_cog.leave_role(mock_ctx,role="bot-dev"))
#
#         #
#         # for role in mock_ctx.author.roles:
#         #     print(role.name)
#
#         self.assertEqual(mock_ctx.author.roles[1].name, expected_test_user.roles[1].name)
#         mock_ctx.send.assert_called_with("fasdfsd")
#
#
#     def test_removing_all_roles_while_joining_alumnus(self):
#         pass
#
#     def test_join_role_to_user(self):
#         '''daco daco daco'''
#         mocked_bot = MockBot()
#         bot_cog = projects.Projects(mocked_bot)
#
#         bot_role = MockRole(name="bot-dev", id=1)
#         muddy_role = MockRole(name="muddy-swamp", id=2)
#
#         test_user = MockMember(name="Jimmy", roles=[bot_role, muddy_role])
#         expected_test_user = MockMember(roles=[muddy_role])
#         expected_role = "muddy-swamp"
#         mock_ctx = MockContext(author=test_user)
#
#         asyncio.run()
#
#         assertMethodIsCalled()
#
# #
# if __name__ == '__main__':
#     unittest.main()
