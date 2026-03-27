import os
import unittest


class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read_api_key_from_env(self):
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        print(f"api__key={api_key}")
        expect_key = "sk-xxxxxx"
        self.assertEqual(expect_key, api_key,"从环境变量读取apikey失败")  # add assertion here


if __name__ == '__main__':
    unittest.main()
