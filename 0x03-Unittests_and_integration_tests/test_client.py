#!/usr/bin/env python3
"""
This module tests client.py
"""
import unittest
from requests import HTTPError
from unittest.mock import PropertyMock, patch, Mock

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD
from parameterized import parameterized, parameterized_class
from utils import access_nested_map as anm


class TestGithubOrgClient(unittest.TestCase):
    """TestClass for GithublientOrg"""

    @parameterized.expand([
        ("google", {"key": "value"}),
        ("abc", {"key": "value"}),
        ("Netflix", {"key": "value"})
    ])
    def test_org(self, org_name, output):
        """Test the GithubOrgClient.org method"""
        expected_url = f"{GithubOrgClient.ORG_URL.format(org=org_name)}"
        with patch('client.get_json', return_value=output) as mock_get_json:
            client = GithubOrgClient(org_name)
            result = client.org
            # print(result)
            mock_get_json.assert_called_once_with(expected_url)
            self.assertEqual(result, output)

    @parameterized.expand([
        ("google", "https://api.github.com/orgs/adobe/repos"),
        ("abc", "https://api.github.com/orgs/abc/repos"),
        ('Netflix', "https://api.github.com/orgs/Netflix/repos")
    ])
    def test_public_repos_url(self, org_name, output):
        """Test the GithubOrgClient.public_r

        epos_url method"""
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = output
            client = GithubOrgClient(org_name)
            result = client._public_repos_url
            self.assertEqual(result, output)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test the GithubOrgClient public_repos method"""
        payload = {
            "repos_url": "https://api.github.com/orgs/google/repos",
            "repos": [
                {
                    "id": 7697149,
                    "node_id": "MDEwOlJlcG9zaXRvcnk3Njk3MTQ5",
                    "name": "episodes.dart",
                    "full_name": "google/episodes.dart",
                    "private": False,
                    "owner": {
                        "login": "google",
                        "id": 1342004,
                    },
                    "forks": 22,
                    "open_issues": 0,
                    "watchers": 12,
                    "default_branch": "master",
                },
                {
                    "id": 7776515,
                    "node_id": "MDEwOlJlcG9zaXRvcnk3Nzc2NTE1",
                    "name": "cpp-netlib",
                    "full_name": "google/cpp-netlib",
                    "private": False,
                    "owner": {
                        "login": "google",
                        "id": 1342004,
                    },
                    "forks": 59,
                    "open_issues": 0,
                    "watchers": 292,
                    "default_branch": "master",
                },
            ]
        }
        # print(anm(payload, (("repos"), )))
        mock_get_json.return_value = payload["repos"]
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as pmock:
            pmock.return_value = payload["repos_url"]
            client = GithubOrgClient("google")
            public_repo = client.public_repos()
            self.assertEqual(public_repo, ["episodes.dart", "cpp-netlib"], )
            pmock.assert_called_once()
        mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, license, key, ret):
        """Tests the has_license static method"""
        repo_to_check = GithubOrgClient.has_license(license, key)
        self.assertEqual(repo_to_check, ret)


test_cases = [
    {
        'org_payload': TEST_PAYLOAD[0][0],
        'repos_payload': TEST_PAYLOAD[0][1],
        'expected_repos': TEST_PAYLOAD[0][2],
        'apache_repos': TEST_PAYLOAD[0][3]
    }
]


@parameterized_class(test_cases)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class"""

    @classmethod
    def setUpClass(cls) -> None:
        """Sets Up the class"""
        routes_payload = {
            "https://api.github.com/orgs/google": cls.org_payload,
            "https://api.github.com/orgs/google/repos": cls.repos_payload
        }

        def get_payload(url):
            if url in routes_payload:
                return Mock(**{'json.return_value': routes_payload[url]})
            return HTTPError

        cls.get_patcher = patch('requests.get', side_effect=get_payload)
        cls.get_patcher.start()

    def test_public_repos(self) -> None:
        """Test the public repo method"""
        client = GithubOrgClient("google")
        public_repos = client.public_repos()
        self.assertEqual(public_repos, self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """test the public_repos method with a license"""
        client = GithubOrgClient("google")
        public_repos = client.public_repos(license="apache-2.0")
        self.assertEqual(public_repos, self.apache_repos)

    @classmethod
    def tearDownClass(cls) -> None:
        """"Tear down the class"""
        cls.get_patcher.stop()


if __name__ == "__main__":
    unittest.main()
