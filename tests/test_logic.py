from unittest import TestCase
import asyncio

import src.match_logic as match_logic


async def client(logic, delay, **info):
    # await asyncio.sleep(delay)

    return await logic.create_match_request(**info)


def is_timeout_response(response):
    return response.get('error', False) == 'timeout'


class TestMatchLogic(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logic = match_logic.MatchLogic()
        cls.loop = asyncio.get_event_loop()

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()

    def test_if_connected_clients_number_is_equal_limit_clients_number(self):
        clients_count = 20
        TestMatchLogic.logic.clients_number = clients_count

        loop = TestMatchLogic.loop
        tasks = [asyncio.ensure_future(client(
            TestMatchLogic.logic, i, **{'nickname': str(i), 'ip': i})) for i in range(clients_count)]
        loop.run_until_complete(asyncio.gather(*tasks))

        self.assertTrue(all([not is_timeout_response(t.result()) for t in tasks]))

    def test_if_connected_clients_number_is_less_than_limit_clients_number(self):
        clients_count = 3
        time_out = 0.001
        TestMatchLogic.logic.clients_number = clients_count
        TestMatchLogic.logic.match_wait_time = time_out

        loop = TestMatchLogic.loop
        tasks = [asyncio.ensure_future(client(
            TestMatchLogic.logic, i, **{'nickname': str(i), 'ip': i})) for i in range(clients_count - 1)]
        loop.run_until_complete(asyncio.gather(*tasks))

        self.assertTrue(all([is_timeout_response(t.result()) for t in tasks]))

    def test_if_many_clients_is_connecting(self):
        clients_count = 5
        time_out = 1
        connecting_count = clients_count * 1000 - 1
        excess_count = connecting_count % clients_count
        TestMatchLogic.logic.clients_number = clients_count
        TestMatchLogic.logic.match_wait_time = time_out

        loop = TestMatchLogic.loop
        tasks = [asyncio.ensure_future(client(
            TestMatchLogic.logic, i, **{'nickname': str(i), 'ip': i})) for i in range(connecting_count)]
        loop.run_until_complete(asyncio.gather(*tasks))

        self.assertTrue(sum([is_timeout_response(t.result()) for t in tasks]) == excess_count)
