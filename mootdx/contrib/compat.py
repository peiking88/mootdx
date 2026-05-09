from opentdx.reader import TdxDailyBarReader


class MooTdxDailyBarReader(TdxDailyBarReader):
    """感谢 bopomofo 的鼎力支持

    SECURITY_TYPE / SECURITY_COEFFICIENT / get_security_type
    均继承自 opentdx TdxDailyBarReader，无需重复定义。
    """
