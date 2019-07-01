import mock
import pytest

from user_sync.rules import RuleProcessor


@pytest.fixture
def rule_processor(caller_options):
    return RuleProcessor(caller_options)


@pytest.fixture
def caller_options():
    return {'adobe_group_filter': None, 'after_mapping_hook': None, 'default_country_code': 'US',
            'delete_strays': False, 'directory_group_filter': None, 'disentitle_strays': False, 'exclude_groups': [],
            'exclude_identity_types': ['adobeID'], 'exclude_strays': False, 'exclude_users': [],
            'extended_attributes': None, 'process_groups': True, 'max_adobe_only_users': 200,
            'new_account_type': 'federatedID', 'remove_strays': True, 'strategy': 'sync',
            'stray_list_input_path': None, 'stray_list_output_path': None,
            'test_mode': True, 'update_user_info': False, 'username_filter_regex': None,
            'adobe_only_user_action': ['remove'], 'adobe_only_user_list': None,
            'adobe_users': ['all'], 'config_filename': 'tests/fixture/user-sync-config.yml',
            'connector': 'ldap', 'encoding_name': 'utf8', 'user_filter': None,
            'users': None, 'directory_connector_type': 'csv',
            'directory_connector_overridden_options': {'file_path': '../tests/fixture/remove-data.csv'},
            'adobe_group_mapped': False, 'additional_groups': []}


@mock.patch('user_sync.helper.CSVAdapter.read_csv_rows')
def test_stray_key_map(csv_reader, rule_processor):
    csv_mock_data = [{'type': 'adobeID', 'username': 'removeuser2@example.com', 'domain': 'example.com'},
                     {'type': 'federatedID', 'username': 'removeuser@example.com', 'domain': 'example.com'},
                     {'type': 'enterpriseID', 'username': 'removeuser3@example.com', 'domain': 'example.com'}]
    csv_reader.return_value = csv_mock_data
    rule_processor.read_stray_key_map('')
    actual_value = rule_processor.stray_key_map
    expected_value = {None: {'federatedID,removeuser@example.com,': None,
                             'enterpriseID,removeuser3@example.com,': None,
                             'adobeID,removeuser2@example.com,': None}}

    assert expected_value == actual_value

    # Added secondary umapi value
    csv_mock_data = [{'type': 'adobeID', 'username': 'remo@sample.com', 'domain': 'sample.com', 'umapi': 'secondary'},
                     {'type': 'federatedID', 'username': 'removeuser@example.com'},
                     {'type': 'enterpriseID', 'username': 'removeuser3@example.com', 'domain': 'example.com'}]
    csv_reader.return_value = csv_mock_data
    rule_processor.read_stray_key_map('')
    actual_value = rule_processor.stray_key_map
    expected_value = {'secondary': {'adobeID,remo@sample.com,': None},
                      None: {'federatedID,removeuser@example.com,': None,
                             'enterpriseID,removeuser3@example.com,': None,
                             'adobeID,removeuser2@example.com,': None}}
    assert expected_value == actual_value


def test_get_user_attribute_difference(rule_processor):
    umapi_users_mock_data = {'email': 'adobe.username@example.com', 'status': 'active',
                             'username': 'adobe.username@example.com', 'domain': 'example.com',
                             'firstname': 'Adobe', 'lastname': 'Username', 'country': 'US',
                             'type': 'federatedID'}

    # Updated user's email, firstname and lastname
    directory_user_mock_data = {'identity_type': 'federatedID', 'username': 'adobeupdate.username2@example.com',
                                'domain': 'example.com', 'firstname': 'Adobeupdate', 'lastname': 'Username2',
                                'email': 'adobeupdate.username2@example.com', 'groups': ['All Sea of Carag'],
                                'country': 'US',
                                'member_groups': [],
                                'source_attributes': {'email': 'adobeupdate.username2@example.com',
                                                      'identity_type': None,
                                                      'username': None, 'domain': None, 'givenName': 'Adobeupdate',
                                                      'sn': 'Username2', 'c': 'US'}}

    actual_difference_value = rule_processor.get_user_attribute_difference(directory_user_mock_data,
                                                                           umapi_users_mock_data)
    expected_difference_value = {'email': 'adobeupdate.username2@example.com', 'firstname': 'Adobeupdate',
                                 'lastname': 'Username2'}
    assert expected_difference_value == actual_difference_value
    # test with no change
    actual_difference_value = rule_processor.get_user_attribute_difference(umapi_users_mock_data, umapi_users_mock_data)
    assert actual_difference_value == {}
