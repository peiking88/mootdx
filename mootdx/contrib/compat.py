from opentdx.reader import TdxDailyBarReader

from mootdx.logger import logger

# 交易所代码: sz=深圳, sh=上海
SECURITY_EXCHANGE = ['sz', 'sh']


class MooTdxDailyBarReader(TdxDailyBarReader):
    """感谢 bopomofo 的鼎力支持"""

    SECURITY_TYPE = [
        'SH_A_STOCK',
        'SH_B_STOCK',
        'SH_STAR_STOCK',
        'SH_INDEX',
        'SH_FUND',
        'SH_BOND',
        'SZ_A_STOCK',
        'SZ_B_STOCK',
        'SZ_INDEX',
        'SZ_FUND',
        'SZ_BOND',
    ]

    SECURITY_COEFFICIENT = {
        'SH_A_STOCK': [0.01, 0.01],
        'SH_B_STOCK': [0.001, 0.01],
        'SH_STAR_STOCK': [0.01, 0.01],
        'SH_INDEX': [0.01, 1.0],
        'SH_FUND': [0.001, 1.0],
        'SH_BOND': [0.001, 1.0],
        'SZ_A_STOCK': [0.01, 0.01],
        'SZ_B_STOCK': [0.01, 0.01],
        'SZ_INDEX': [0.01, 1.0],
        'SZ_FUND': [0.001, 0.01],
        'SZ_BOND': [0.001, 0.01],
    }

    def get_security_type(self, fname):

        exchange = str(fname[-12:-10]).lower()
        code_head = fname[-10:-8]

        if exchange == SECURITY_EXCHANGE[0]:
            if code_head in ['00', '30']:
                return 'SZ_A_STOCK'

            if code_head in ['20']:
                return 'SZ_B_STOCK'

            if code_head in ['39']:
                return 'SZ_INDEX'

            if code_head in ['15', '16', '18']:
                return 'SZ_FUND'

            if code_head in ['10', '11', '12', '13', '14']:
                return 'SZ_BOND'

            return 'SZ_OTHER'

        if exchange == SECURITY_EXCHANGE[1]:
            if code_head in ['60']:
                return 'SH_A_STOCK'

            if code_head in ['90']:
                return 'SH_B_STOCK'

            if code_head in ['68']:
                return 'SH_STAR_STOCK'

            if code_head in ['00', '88', '99']:
                return 'SH_INDEX'

            if code_head in ['50', '51', '58']:
                return 'SH_FUND'

            if code_head in ['01', '02', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']:
                return 'SH_BOND'

            return 'SH_OTHER'

        logger.error('Unknown security exchange !\n')
        raise NotImplementedError
