"""玩家自服务指令路由：修改工牌名（#改工牌 / #改名）。

QQ 官方机器人下拿不到群成员昵称（平台灰度接口多数未开放），玩家名字会退化为
QQ 昵称 / openid。这里给玩家一个主动改自己展示名（工牌名）的入口，写入
players.custom_name，展示优先级最高（见 logic.name_of）。
"""

import asyncio
import re

from ..core import logic
from ..core.result import R
from .base import Route, gid_of

_NAME_MAX = 20


def _parse_name(event) -> str:
    """从消息里取出 #改工牌/#改名 之后的名字（支持半角/全角 # 与空格/无空格）。"""
    s = (event.message_str or "").strip()
    m = re.match(r"^[#＃](?:改工牌|改名)\s*(.*)$", s)
    if not m:
        return ""
    return (m.group(1) or "").strip()


async def rename(ctx, event):
    gid = gid_of(event)
    uid = str(event.get_sender_id())
    new_name = _parse_name(event)

    p = await asyncio.to_thread(ctx.db.get_player_row, gid, uid)
    if not p:
        return R(err="你还没有入职档案，先发条任意指令建号再来改名吧～")

    cur = logic.name_of(p)
    if not new_name:
        # 不带名字：回显当前工牌名 + 用法提示，不落库
        return R(text=f"你当前的工牌名是「{cur}」\n改名请发送：#改工牌 新名字")

    if len(new_name) > _NAME_MAX:
        new_name = new_name[:_NAME_MAX]

    await asyncio.to_thread(ctx.db.set_custom_name, gid, uid, new_name)
    return R(text=f"工牌名已更新为「{new_name}」🪪（原名「{cur}」）")


ROUTES = [
    Route(
        r"^#(?:改工牌|改名)(?:\s+\S.*)?\s*$",
        "cmd_rename",
        "修改自己的工牌名（展示昵称），QQ官方机器人下也能用",
        rename,
    ),
]
