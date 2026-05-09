import asyncio
import hashlib
from functools import partial
from pathlib import Path

from mootdx.financial import financial
from mootdx.logger import logger
from mootdx.utils import TqdmUpTo


def download(downdir, filename):
    """
    带进度条下载函数
    :param downdir:
    :param filename:
    :return:
    """

    with TqdmUpTo(unit='B', unit_scale=True, miniters=1, ascii=True) as t:
        financial.Financial().fetch_only(report_hook=t.update_to, filename=filename, downdir=downdir)

    return True


async def fetch_file(downdir, file_obj):
    """
    下载文件

    :param downdir:
    :param file_obj: 文件对象
    :return:
    """

    filepath = Path(downdir) / file_obj['filename']

    # 判断文件是否存在, 验证文件名和哈希值
    if filepath.exists() and file_obj['hash'] == hashlib.md5(open(filepath, 'rb').read()).hexdigest():
        logger.warning(f'文件已经存在: {filepath}')
        return None

    result = await asyncio.get_event_loop().run_in_executor(
        None,
        partial(financial.Financial().fetch_only, report_hook=None, filename=file_obj['filename'], downdir=downdir),
    )

    return result


class Affair(object):
    @staticmethod
    def _parse_with_opentdx(filepath, **kwargs):
        """使用 opentdx HistoryFinancialCrawler 解析财务数据文件"""
        from opentdx import HistoryFinancialCrawler

        crawler = HistoryFinancialCrawler()
        result = crawler.fetch_and_parse(path_to_download=str(filepath.parent),
                                         reporthook=None, filename=filepath.name)
        if result is not None:
            return HistoryFinancialCrawler.to_df(result)
        return None

    @staticmethod
    def parse(downdir='.', filename=None, **kwargs):
        """
        按目录解析文件。优先使用 opentdx 解析器，失败则回退到内置实现。

        :param downdir: 下载目录
        :param filename: 文件名
        :return: DataFrame or None
        """

        if not filename:
            logger.critical('文件名不能为空!')
            return None

        filepath = Path(downdir) / filename
        filepath.exists() or Affair.fetch(downdir, filename)

        if not Path(filepath).exists():
            logger.warning(f'文件不存在：{filename}')
            return None

        try:
            result = Affair._parse_with_opentdx(filepath, **kwargs)
            if result is not None and not result.empty:
                return result
        except Exception:
            logger.debug('opentdx 解析失败，回退到内置解析器')

        return financial.FinancialReader().to_data(filepath, **kwargs)

    @staticmethod
    def files():
        """
        财务文件列表

        :return:
        """

        history = financial.FinancialList()
        results = history.fetch_and_parse()

        return results

    @staticmethod
    def fetch(downdir: str = None, filename: str = None):  # noqa
        """
        财务数据下载

        :param downdir: 下载目录
        :param filename: 文件名
        :return:
        """

        history = financial.FinancialList()
        crawler = financial.Financial()
        downdir = downdir or '.'  # noqa

        if not Path(downdir).is_dir():
            logger.warning('下载目录不存在, 进行创建.')
            Path(downdir).mkdir(parents=True)

        if filename:
            logger.debug(f'下载文件 {filename}.')

            with TqdmUpTo(unit='B', unit_scale=True, miniters=1, ascii=True) as t:
                crawler.fetch_only(report_hook=t.update_to, filename=filename, downdir=downdir)

            return True

        tasks = []
        event = asyncio.get_event_loop()

        for x in history.fetch_and_parse():
            task = event.create_task(fetch_file(file_obj=x, downdir=downdir))
            tasks.append(task)

        event.run_until_complete(asyncio.wait(tasks))
