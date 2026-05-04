import configparser
from pathlib import Path

from mootdx.logger import logger

TDX_SEARCH_PATHS = [
    Path.home() / '.local/share/tdxcfv/drive_c/tc',
    Path.home() / '.wine/drive_c/new_tdx',
    Path('C:/new_tdx'),
]


def find_tdx_dir():
    for p in TDX_SEARCH_PATHS:
        cfg = p / 'connect.cfg'
        if cfg.exists():
            return p
    return None


def parse_connect_cfg(path=None):
    if path is None:
        tdx_dir = find_tdx_dir()
        if tdx_dir is None:
            return None
        path = tdx_dir / 'connect.cfg'

    if not Path(path).exists():
        return None

    cp = configparser.ConfigParser()
    cp.read(str(path), encoding='gbk')

    result = {}

    for section, key in [('HQHOST', 'HQ'), ('DSHOST', 'EX'), ('HFHost', 'HF'), ('INFOHOST2', 'INFO')]:
        hosts = []
        i = 1
        while True:
            ip = cp.get(section, f'IPAddress{i:02d}', fallback=None)
            if not ip:
                break
            port = cp.getint(section, f'Port{i:02d}', fallback=7709)
            name = cp.get(section, f'HostName{i:02d}', fallback=f'server{i}')
            hosts.append((name, ip, port))
            i += 1
        if hosts:
            result[key] = hosts

    return result


def update_servers_from_tdx():
    servers = parse_connect_cfg()
    if servers is None:
        return False

    from mootdx import config
    from mootdx.consts import HQ_HOSTS, EX_HOSTS

    current = config.get('SERVER')
    changed = False

    for key in ('HQ', 'EX'):
        if key in servers and servers[key] != current.get(key):
            current[key] = servers[key]
            changed = True

    if 'HF' in servers:
        current['HF'] = servers['HF']
        changed = True

    if changed:
        logger.info(f'从通达信配置更新了服务器列表: {list(servers.keys())}')

    return changed
