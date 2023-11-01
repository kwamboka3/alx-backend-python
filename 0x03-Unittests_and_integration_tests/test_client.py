import unittest
from parameterized import parameterized
from unittest.mock import patch
from client import GithubOrgClient

class TestGithubOrgClient(unittest.TestCase):

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch('client.GithubOrgClient.get_json', return_value={'key': 'value'})
    def test_org(self, org_name, mock_get_json):
        client = GithubOrgClient(org_name)
        result = client.org()
        self.assertEqual(result, {'key': 'value'})
        mock_get_json.assert_called_once_with(f'https://api.github.com/orgs/{org_name}')

if __name__ == '__main__':
    unittest.main()

