import unittest
from unittest.mock import patch, mock_open
from io import StringIO
import ip_print


class TestIpPrintExecute(unittest.TestCase):
    @patch("sys.argv", ["ip_print.py", "mocked_filename.json"])
    @patch("builtins.open", new_callable=mock_open, read_data='{"vm_private_ips": {"value": {"name": "192.168.101.101"}}}')
    @patch("sys.stdout", new_callable=StringIO)
    def test_execute_success(self, mock_stdout, mock_file):
        # Call the main function
        with self.assertRaises(SystemExit) as cm:
            ip_print.execute()

        # Check the exit code and output
        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(mock_stdout.getvalue().strip(), "192.168.101.101")

    @patch("sys.stdout", new_callable=StringIO)
    def test_execute_with_no_filename_argument(self, mock_stdout):
        # Call the main function
        with self.assertRaises(SystemExit) as cm:
            ip_print.execute()

        # Check the exit code
        self.assertEqual(cm.exception.code, 1)

    @patch("sys.argv", ["ip_print.py", "mocked_filename.json"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_execute_with_file_not_existing(self, mock_stdout):
        # Call the main function
        with self.assertRaises(SystemExit) as cm:
            ip_print.execute()

        # Check the exit code and output
        self.assertEqual(cm.exception.code, 2)

    @patch("sys.argv", ["ip_print.py", "mocked_filename.json"])
    @patch("builtins.open", new_callable=mock_open, read_data='{')
    @patch("sys.stdout", new_callable=StringIO)
    def test_execute_with_incorrect_data(self, mock_file, mock_stdout):
        # Call the main function
        with self.assertRaises(SystemExit) as cm:
            ip_print.execute()

        # Check the exit code and output
        self.assertEqual(cm.exception.code, 3)

    @patch("sys.argv", ["ip_print.py", "mocked_filename.json"])
    @patch("builtins.open", new_callable=mock_open, read_data='{"incomplete": "data"}')
    @patch("sys.stdout", new_callable=StringIO)
    def test_execute_with_incomplete_json_data(self, mock_file, mock_stdout):
        # Call the main function
        with self.assertRaises(SystemExit) as cm:
            ip_print.execute()

        # Check the exit code and output
        self.assertEqual(cm.exception.code, 4)

    @patch("sys.argv", ["ip_print.py", "mocked_filename.json"])
    @patch("builtins.open", new_callable=mock_open, read_data='{"vm_private_ips": {"value": {}}}')
    @patch("sys.stdout", new_callable=StringIO)
    def test_execute_with_empty_data(self, mock_file, mock_stdout):
        # Call the main function
        with self.assertRaises(SystemExit) as cm:
            ip_print.execute()

        # Check the exit code and output
        self.assertEqual(cm.exception.code, 5)


class TestIpPrintGetIps(unittest.TestCase):
    def test_get_ips_success_with_no_network_ips(self):
        sample_data = {
            "vm_private_ips": {
                "value": {
                    "name1": "192.168.101.101",
                    "name2": "192.168.101.102"
                }
            }
        }
        ip_addresses, error = ip_print.get_ips(sample_data)
        self.assertIsNone(error)
        self.assertEqual(ip_addresses, ["192.168.101.101", "192.168.101.102"])

        sample_data_with_empty_network = {
            "vm_private_ips": {
                "value": {
                    "name1": "192.168.101.100",
                    "name2": "192.168.101.102"
                },
                "network": {}
            }
        }
        ip_addresses, error = ip_print.get_ips(sample_data_with_empty_network)
        self.assertIsNone(error)
        self.assertEqual(ip_addresses, ["192.168.101.100", "192.168.101.102"])

        sample_data_with_empty_vms = {
            "vm_private_ips": {
                "value": {
                    "name1": "192.168.101.101",
                    "name2": "192.168.101.103"
                },
                "network": {"vms": []}
            }
        }
        ip_addresses, error = ip_print.get_ips(sample_data_with_empty_vms)
        self.assertIsNone(error)
        self.assertEqual(ip_addresses, ["192.168.101.101", "192.168.101.103"])

    def test_get_ips_success_with_correct_network_data(self):
        sample_data_not_matching_network = {
            "vm_private_ips": {
                "value": {
                    "name1": "192.168.101.101",
                    "name2": "192.168.101.102"
                }
            },
            "network": {
                "vms": [
                    {
                        "attributes": {
                            "name": "name3",
                            "access_ip_v4": "10.0.0.87",
                            "availability_zone": "zoneA"
                        }
                    }
                ]
            }
        }
        ip_addresses, error = ip_print.get_ips(sample_data_not_matching_network)
        self.assertIsNone(error)
        self.assertEqual(ip_addresses, ["192.168.101.101", "192.168.101.102"])

        sample_data_some_matching = {
            "vm_private_ips": {
                "value": {
                    "name1": "192.168.101.101",
                    "name2": "192.168.101.102",
                    "name3": "192.168.101.103",
                }
            },
            "network": {
                "vms": [
                    {
                        "attributes": {
                            "name": "name3",
                            "access_ip_v4": "10.0.0.87",
                        }
                    },
                    {
                        "attributes": {
                            "name": "name2",
                            "access_ip_v4": "10.0.0.88",
                        }
                    }
                ]
            }
        }
        ip_addresses, error = ip_print.get_ips(sample_data_some_matching)
        self.assertIsNone(error)
        self.assertEqual(ip_addresses, ["192.168.101.101", "192.168.101.102 10.0.0.88", "192.168.101.103 10.0.0.87"])

        sample_data_all_matching = {
            "vm_private_ips": {
                "value": {
                    "name1": "192.168.101.101",
                    "name2": "192.168.101.102",
                    "name3": "192.168.101.103",
                }
            },
            "network": {
                "vms": [
                    {
                        "attributes": {
                            "name": "name3",
                            "access_ip_v4": "10.0.0.87",
                        }
                    },
                    {
                        "attributes": {
                            "name": "name1",
                            "access_ip_v4": "10.0.0.89",
                        }
                    },
                    {
                        "attributes": {
                            "name": "name2",
                            "access_ip_v4": "10.0.0.88",
                        }
                    }
                ]
            }
        }
        ip_addresses, error = ip_print.get_ips(sample_data_all_matching)
        self.assertIsNone(error)
        self.assertEqual(ip_addresses, ["192.168.101.101 10.0.0.89", "192.168.101.102 10.0.0.88", "192.168.101.103 10.0.0.87"])

    def test_get_ips_success_with_empty_data(self):
        sample_data = {
            "vm_private_ips": {
                "value": {}
            }
        }
        ip_addresses, error = ip_print.get_ips(sample_data)
        self.assertIsNone(error)
        self.assertEqual(len(ip_addresses), 0)

    def test_get_ips_missing_ips(self):
        sample_data = {"incomplete": "data"}
        ip_addresses, error = ip_print.get_ips(sample_data)
        self.assertIsNone(ip_addresses)
        self.assertIsInstance(error, KeyError)

    def test_get_ips_with_wrong_network_data(self):
        sample_data_contain_attribute_with_no_name = {
            "vm_private_ips": {
                "value": {
                    "name1": "192.168.101.101",
                    "name2": "192.168.101.102",
                    "name3": "192.168.101.103",
                }
            },
            "network": {
                "vms": [
                    {
                        "attributes": {
                            "access_ip_v4": "10.0.0.87",
                        }
                    },
                ]
            }
        }
        ip_addresses, error = ip_print.get_ips(sample_data_contain_attribute_with_no_name)
        self.assertIsNone(ip_addresses)
        self.assertIsInstance(error, KeyError)

        sample_data_contain_attribute_with_no_access_ip_v4 = {
            "vm_private_ips": {
                "value": {
                    "name1": "192.168.101.101",
                    "name2": "192.168.101.102",
                    "name3": "192.168.101.103",
                }
            },
            "network": {
                "vms": [
                    {
                        "attributes": {
                            "name": "name",
                        }
                    },
                ]
            }
        }
        ip_addresses, error = ip_print.get_ips(sample_data_contain_attribute_with_no_access_ip_v4)
        self.assertIsNone(ip_addresses)
        self.assertIsInstance(error, KeyError)


if __name__ == '__main__':
    unittest.main()