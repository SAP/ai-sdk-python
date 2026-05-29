from __future__ import annotations
from typing import Optional
import json
import pathlib
from urllib.parse import urlparse

from ai_core_sdk.credentials import CORE_CREDENTIAL_VALUES, get_nested_value
from ai_core_sdk.helpers import get_home
from ai_core_sdk.helpers.constants import AI_CORE_PREFIX

import click

# Constants
MAX_TRIES = 5
OAUTH_TOKEN_SUFFIX = '/oauth/token'
API_V2_SUFFIX = '/v2'
DEFAULT_CONFIG = 'config.json'
DEFAULT_RESOURCE_GROUP = 'default'
DEFAULT_PROFILE = 'default'

# Utility Functions
def create_config(**kwargs):
    return {f'{AI_CORE_PREFIX}_{k}'.upper(): v for k, v in kwargs.items() if v is not None}

def is_valid_url(url, path_forbidden=True):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, not result.path if path_forbidden else True])
    except ValueError:
        return False

def prompt_for_input(prompt_text, is_url=False, path_forbidden=True):
    url = None
    for _ in range(MAX_TRIES):
        user_input = click.prompt(prompt_text, type=str).rstrip('/')
        if is_url and not is_valid_url(user_input, path_forbidden):
            click.echo('Input is not a valid URL.')
            if path_forbidden:
                click.echo('Enter URL without any additional path or trailing slash.')
        else:
            url = user_input
            break

    if url is None:
        raise ValueError('Max tries reached!')
    return url

# CLI Functions
@click.group()
@click.option('-p', '--profile', default=DEFAULT_PROFILE, type=str)
@click.pass_context
def cli(ctx, profile):
    """CLI group for the AI Core SDK"""
    ctx.ensure_object(dict)
    ctx.obj['profile'] = profile


def load_service_key(service_key_json: str):
    with pathlib.Path(service_key_json).open() as stream:
        service_key = json.load(stream)
    kwargs = {}
    for value in CORE_CREDENTIAL_VALUES:
        # In VCAP the service_key is nested under credentials
        # We can reuse the vcap_name from the CREDENTIAL_VALUES
        # when parsing the service_key
        # skip if vcap_key not defined
        if not value.vcap_key:
            continue
        try:
            kwargs[value.name] = get_nested_value(service_key, value.vcap_key[1:])
        except KeyError:
            kwargs[value.name] = None
    return kwargs

def get_auth_url(auth_url: Optional[str]=None):
    auth_url = auth_url or prompt_for_input('Please enter the authorization URL', is_url=True, path_forbidden=False)
    if auth_url.endswith(OAUTH_TOKEN_SUFFIX):
        return auth_url
    else:
        return auth_url + OAUTH_TOKEN_SUFFIX

def get_base_url(base_url: Optional[str]=None):
    base_url = base_url or prompt_for_input('Please enter the base API URL', is_url=True, path_forbidden=False)
    if base_url.endswith(API_V2_SUFFIX):
        return base_url
    else:
        return base_url + API_V2_SUFFIX


def get_str_value(msg: str, value: Optional[str]=None):
    return value or click.prompt(msg, type=str)

def confirm_resource_group(resource_group: Optional[str]=None):
    if resource_group is None:
        resource_group = click.prompt('Please confirm or enter the AICore resource group', default=DEFAULT_RESOURCE_GROUP, type=str)
    return resource_group

def get_profile_config_path(profile: str):
    profile = profile if profile != DEFAULT_PROFILE and profile is not None else None
    home = pathlib.Path(get_home())
    home.mkdir(parents=True, exist_ok=True)
    config_path = home / (DEFAULT_CONFIG if profile is None else f'config_{profile.lower()}.json')
    if profile is not None:
        click.echo(f'Remember to set `{AI_CORE_PREFIX}_PROFILE={profile.lower()}` to use your profile.')
    return config_path


def create_config_file(config_path: pathlib.Path, auth_url: str, client_id: str, client_secret: str,
                       cert_file_path: pathlib.Path, key_file_path: pathlib.Path, base_url: str, resource_group: str):
    config = create_config(auth_url=auth_url, client_id=client_id, client_secret=client_secret,
                           cert_file_path=cert_file_path, key_file_path=key_file_path, base_url=base_url,
                           resource_group=resource_group)
    if config_path.exists() and not click.confirm(f'A config file {config_path} already exists. Do you want to replace it?'):
        exit()
    click.echo(f'Creating new config {config_path}')
    with config_path.open('w') as stream:
        json.dump(config, stream, indent=4)


@cli.command()
@click.option('-a', '--auth-url', default=None, type=str)
@click.option('-s', '--client-secret', default=None, type=str)
@click.option('-i', '--client-id', default=None, type=str)
@click.option('-cf', '--cert-file-path', default=None, type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-kf', '--key-file-path', default=None, type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-u', '--base-url', default=None, type=str)
@click.option('-g', '--resource-group', default=None, type=str)
@click.option('-k', '--service-key-json', default=None, type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.pass_context
def configure(ctx, auth_url, client_secret, client_id, cert_file_path, key_file_path, base_url, resource_group,
              service_key_json):
    profile = ctx.obj['profile']
    if service_key_json:
        service_key_json = load_service_key(service_key_json)
    else:
        service_key_json = {}

    base_url = get_base_url(service_key_json.get('base_url', base_url))
    auth_url = get_auth_url(service_key_json.get('auth_url', auth_url))
    cert_url = service_key_json.get('cert_url', None)
    if cert_url:
        auth_url = get_auth_url(cert_url)
    client_id = get_str_value('Please enter the client ID', service_key_json.get('client_id', client_id))

    client_secret = service_key_json.get('client_secret', client_secret)
    cert_file_path = service_key_json.get('cert_file_path', cert_file_path)
    key_file_path = service_key_json.get('key_file_path', key_file_path)

    if not (client_secret is not None or (key_file_path is not None or cert_file_path is not None)):
        client_secret = get_str_value(
            'Please enter the client secret (skip, if you\'re going to provide X.509 credentials',
            service_key_json.get('client_secret', client_secret))
        cert_file_path = get_str_value('Please enter path to the X.509 certificate file',
                                       service_key_json.get('cert_file_path', cert_file_path))
        key_file_path = get_str_value('Please enter path to the X.509 key file',
                                      service_key_json.get('key_file_path', key_file_path))
    resource_group = confirm_resource_group(resource_group)
    create_config_file(
        config_path=get_profile_config_path(profile),
        auth_url=auth_url,
        client_id=client_id,
        client_secret=client_secret,
        cert_file_path=cert_file_path,
        key_file_path=key_file_path,
        base_url=base_url,
        resource_group=resource_group
    )



if __name__ == "__main__":
    cli() #pylint: disable = no-value-for-parameter
