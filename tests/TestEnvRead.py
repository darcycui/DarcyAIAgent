import os
import unittest


class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read_api_key_from_env(self):
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        expect_key = "sk-5e22596a4fbe4189a037b94704fa3e10"
        self.assertEqual(expect_key, api_key,"从环境变量读取apikey失败")  # add assertion here


if __name__ == '__main__':
    unittest.main()
