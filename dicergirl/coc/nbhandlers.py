from .investigator import Investigator
from .coccards import coc_cards, coc_cache_cards, coc_rolls
from .cocutils import sc, ti, li

try:
    from ..utils.utils import format_msg, get_status, on_startswith, format_str
    from ..utils.parser import CommandParser, Commands, Only, Optional, Required
except ImportError:
    from dicergirl.utils.utils import format_msg, get_status, on_startswith, format_str
    from dicergirl.utils.parser import CommandParser, Commands, Only, Optional, Required

from nonebot.matcher import Matcher
from nonebot.adapters import Bot as Bot
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.internal.matcher.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

coccommand = on_startswith(".coc", priority=1, block=True).handle()
ticommand = on_startswith(".ti", priority=2, block=True).handle()
licommand = on_startswith(".li", priority=2, block=True).handle()
sccommand = on_startswith(".sc", priority=2, block=True).handle()

async def coc_handler(matcher: Matcher, event: GroupMessageEvent):
    """ COC 车卡指令 """
    if not get_status(event):
        return

    args = format_msg(event.get_message(), begin=".coc", zh_en=True)
    qid = event.get_user_id()
    commands = CommandParser(
        Commands([
            Only("cache", False),
            Optional("set", int),
            Optional("age", int, 20),
            Optional("name", str),
            Optional("sex", str, "女"),
            Optional("roll", int, 1)
            ]),
        args=args,
        auto=True
        ).results
    toroll = commands["roll"]

    if commands["set"]:
        coc_cards.update(event, coc_rolls[qid][commands["set"]], save=True)
        inv = Investigator().load(coc_rolls[qid][commands["set"]])
        await matcher.send(f"使用序列 {commands['set']} 卡:\n{inv.output()}")
        coc_rolls[qid] = {}
        return

    age = commands["age"]
    name = commands["name"]

    if not (15 <= age and age < 90):
        await matcher.send(Investigator().age_change(age))
        return

    reply = ""
    if qid in coc_rolls.keys():
        rolled = len(coc_rolls[qid].keys())
    else:
        coc_rolls[qid] = {}
        rolled = 0

    for i in range(toroll):
        inv = Investigator()
        inv.age_change(age)
        inv.sex = commands["sex"]

        if name:
            inv.name = name

        coc_rolls[qid][rolled+i] = inv.__dict__
        count = inv.rollcount()
        reply += f"天命编号: {rolled+i}\n"
        reply += inv.output() + "\n"
        reply += f"共计: {count[0]}/{count[1]}\n"

    if toroll == 1:
        coc_cache_cards.update(event, inv.__dict__, save=False)

    reply.rstrip("\n")
    await matcher.send(reply)

async def ticommandhandler(matcher: Matcher, event: MessageEvent):
    """ COC 临时疯狂检定指令 """
    if not get_status(event):
        return

    try:
        await matcher.send(ti())
    except:
        await matcher.send("[Oracle] 未知错误, 执行`.debug on`获得更多信息.")

async def licommandhandler(matcher: Matcher, event: MessageEvent):
    """ COC 总结疯狂检定指令 """
    if not get_status(event):
        return

    try:
        await matcher.send(li())
    except:
        await matcher.send("[Oracle] 未知错误, 执行`.debug on`获得更多信息.")

async def sccommandhandler(matcher: Matcher, event: GroupMessageEvent):
    """ COC 疯狂检定指令 """
    if not get_status(event):
        return

    args = format_str(event.get_message(), begin=".sc")
    scrs = sc(args, event)

    if isinstance(scrs, list):
        for scr in scrs:
            await matcher.send(scr)
    else:
        await matcher.send(scrs)

commands = {
    "coccommand": "coc_handler",
    "ticommand": "ticommandhandler",
    "licommand": "licommandhandler",
    "sccommand": "sccommandhandler"
    }