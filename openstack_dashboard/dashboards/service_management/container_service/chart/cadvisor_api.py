
import requests
import json
from requests.adapters import ConnectionError
import datetime
from docker import Client

MAX_URI_LEN = 8192
USER_AGENT = 'openstack-dashboard'

# ENDPOINT_URL = u'http://localhost:8080/api/'


def request(url, method, body=None, headers=None, **kwargs):
    """Request without authentication."""

    content_type = kwargs.pop('content_type', None) or 'application/json'
    headers = headers or {}
    headers.setdefault('Accept', content_type)

    if body:
        headers.setdefault('Content-Type', content_type)

    headers['User-Agent'] = USER_AGENT
    try:
        resp = requests.request(
            method,
            url,
            data=body,
            headers=headers,
            **kwargs)
    except:
        raise ConnectionError
    return resp, resp.text


def get_date_from_input(date_input):
    if date_input is None:
        return None
    elif not date_input:
        return "none"
    else:
        try:
            return datetime.datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            return None


class InputError(Exception):
    pass


def check_is_valid_date(string_date_check):
    if string_date_check == 'none':
        return True
    else:
        try:
            datetime.datetime.strptime(string_date_check, "%Y-%m-%d")
            return True
        except ValueError:
            return False


def get_all_container_data(host_ip, date_from=None, date_to=None):
    endpoint = u'http://' + host_ip + ':8080/api/v1.2/docker/'
    try:
        resp, reply_body = request(endpoint, method="GET", body={})
        status_code = resp.status_code
        if status_code in (requests.codes.ok,
                           requests.codes.created,
                           requests.codes.accepted,
                           requests.codes.no_content):
            data = json.loads(reply_body)
            return data
        else:
            return "Error"
    except ConnectionError:
        return "Error"


def get_container_detail(host_ip, container_id, date_from=None, date_to=None):
    cadvisor_endpoint = u'http://' + host_ip +\
        ":8080/api/v2.0/stats/" + container_id + "?type=docker"
    docker_endpoint = "tcp://" + host_ip + ":2376"
    container_data = {"id": container_id}
    try:
        cli = Client(base_url=docker_endpoint)
        container_data['name'] = cli.containers(
            filters={"id": container_id})[0]['Names'][0]
        resp, reply_body = request(cadvisor_endpoint, method="GET", body={})
        status_code = resp.status_code
        if status_code in (requests.codes.ok,
                           requests.codes.created,
                           requests.codes.accepted,
                           requests.codes.no_content):
            container_data['realtime_data'] = json.loads(reply_body)

            return container_data
        else:
            return "Error"
    except Exception:
        return "Error"


def get_container_list(host_ip):
    endpoint = "tcp://" + host_ip + ":2376"
    try:
        cli = Client(base_url=endpoint)
        return cli.containers()
    except Exception:
        return "Error"
