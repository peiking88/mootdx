from pathlib import Path

from mootdx.logger import logger

TDX_SEARCH_PATHS = [
    Path.home() / '.local/share/tdxcfv/drive_c/tc',
    Path.home() / '.wine/drive_c/new_tdx',
    Path('C:/new_tdx'),
]

SECTION_MAP = {
    'HQHOST': 'HQ',
    'DSHOST': 'EX',
    'HFHost': 'HF',
    'INFOHOST2': 'INFO',
}


def find_tdx_dir():
    for p in TDX_SEARCH_PATHS:
        cfg = p / 'connect.cfg'
        if cfg.exists():
            return p
    return None


def _parse_with_opentdx(path):
    """使用 opentdx TdxConnectCfgReader 解析 connect.cfg"""
    from opentdx import TdxConnectCfgReader

    try:
        reader = TdxConnectCfgReader(cfg_path=str(path), auto_detect=False)
    except Exception:
        return None

    if not reader.is_loaded:
        return None

    all_servers = reader.get_all_servers()
    if not all_servers:
        return None

    result = {}
    for section_key, hosts in all_servers.items():
        mapped_key = SECTION_MAP.get(section_key, section_key)
        result[mapped_key] = [
            (h.get('hostname', h.get('ip', '')), h['ip'], h['port'])
            for h in hosts
        ]

    return result if result else None


def _parse_with_configparser(path):
    """使用 configparser 解析 connect.cfg（回退方案）"""
    import configparser

    if not Path(path).exists():
        return None

    cp = configparser.ConfigParser()
    try:
        cp.read(str(path), encoding='gbk')
    except Exception:
        return None

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


def parse_connect_cfg(path=None):
    """解析通达信 connect.cfg 获取服务器配置

    优先使用 opentdx TdxConnectCfgReader，失败则回退 configparser。
    """
    if path is None:
        tdx_dir = find_tdx_dir()
        if tdx_dir is None:
            return None
        path = tdx_dir / 'connect.cfg'

    result = _parse_with_opentdx(path)
    if result:
        return result

    return _parse_with_configparser(path)


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
