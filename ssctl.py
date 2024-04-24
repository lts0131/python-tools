#!/usr/bin/python3

import urllib3
import base64
import json
from subprocess import call
import click

config_file = '/home/lts/config-ssr.json'


def fetch_rss():
    http = urllib3.PoolManager()
    r = http.request('GET', '')
    rss = base64.b64decode(r.data.decode() + '==').decode()

    ssrs = rss.split('\n')
    ssrs = ssrs[0:-1]
    return ssrs


def parse(ssr):
    base64_encode_str = ssr[6:]
    return parse_ssr(base64_encode_str)


def parse_ssr(base64_encode_str):
    decode_str = base64_decode(base64_encode_str)
    parts = decode_str.split(':')
    if len(parts) != 6:
        print('不能解析SSR链接: %s' % base64_encode_str)
        return

    server = parts[0]
    port = parts[1]
    protocol = parts[2]
    method = parts[3]
    obfs = parts[4]
    password_and_params = parts[5]

    password_and_params = password_and_params.split("/?")

    password_encode_str = password_and_params[0]
    password = base64_decode(password_encode_str)
    params = password_and_params[1]

    param_parts = params.split('&')

    param_dic = {}
    for part in param_parts:
        key_and_value = part.split('=')
        param_dic[key_and_value[0]] = key_and_value[1]

    obfsparam = base64_decode(param_dic['obfsparam'])
    protoparam = base64_decode(param_dic['protoparam'])
    remarks = base64_decode(param_dic['remarks'])
    group = base64_decode(param_dic['group'])

    ssr_dict = {}
    ssr_dict['server'] = server
    ssr_dict['remarks'] = remarks
    ssr_dict['server_port'] = int(port)
    ssr_dict['local_address'] = '127.0.0.1'
    ssr_dict['local_port'] = 1080

    ssr_dict['password'] = password
    ssr_dict['method'] = method
    ssr_dict['protocol'] = protocol
    ssr_dict['protocol_param'] = protoparam
    ssr_dict['obfs'] = obfs
    ssr_dict['obfs_param'] = obfsparam

    return ssr_dict


def fill_padding(base64_encode_str):
    need_padding = len(base64_encode_str) % 4 != 0

    if need_padding:
        missing_padding = 4 - need_padding
        base64_encode_str += '=' * missing_padding
    return base64_encode_str


def base64_decode(base64_encode_str):
    base64_encode_str = fill_padding(base64_encode_str)
    return base64.urlsafe_b64decode(base64_encode_str).decode('utf-8')


def stop_ss():
    call(['/home/lts/shadowsocksr/shadowsocks/local.py',
          '-c',
          config_file, '--pid-file',
          '/home/lts/shadowsocksr.pid',
          '--log-file',
          '/home/lts/shadowsocksr.log',
          '-d',
          'stop'])


def start_ss():
    call(['/home/lts/shadowsocksr/shadowsocks/local.py',
          '-c',
          config_file, '--pid-file',
          '/home/lts/shadowsocksr.pid',
          '--log-file',
          '/home/lts/shadowsocksr.log',
          '-b',
          '0.0.0.0',
          '-d',
          'start'])


def write_config_file(config):
    with open(config_file, 'w') as fp:
        json.dump(config, fp)


def print_ssr_configs(ssr_configs):
    print('servers: ')
    for i in range(len(ssr_configs)):
        print('\t({}) {}'.format(i, ssr_configs[i]['remarks']))


def set_new_config():
    ssrs = fetch_rss()
    ssr_configs = [parse(ssr) for ssr in ssrs if ssr.startswith('ssr://')]

    print_ssr_configs(ssr_configs)

    server_index = int(input('which one: '))

    write_config_file(ssr_configs[server_index])


def current_config():
    with open(config_file, 'r') as fp:
        config = json.load(fp)
        print(json.dumps(config, indent=4))


@click.group()
def cli():
    pass


@click.command()
def start():
    start_ss()


@click.command()
def stop():
    stop_ss()


@click.command()
@click.option('--list', '-l', is_flag=True, default=False)
@click.option('--refresh', '-r', is_flag=True, default=False)
def config(list, refresh):
    if list:
        current_config()
    if refresh:
        stop_ss()
        set_new_config()
        start_ss()


@click.command()
@click.option('--refresh', '-r', is_flag=True, default=False)
def restart(refresh):
    stop_ss()
    if refresh:
        set_new_config()
    start_ss()


cli.add_command(start)
cli.add_command(stop)
cli.add_command(restart)
cli.add_command(config)

if __name__ == '__main__':
    cli()
