from endstone.command import Command, CommandSender
from endstone.plugin import Plugin
from endstone import ColorFormat,Player
from endstone.event import event_handler, BlockBreakEvent,PlayerInteractEvent,ActorKnockbackEvent,BlockPlaceEvent,PlayerCommandEvent,PlayerJoinEvent,PlayerChatEvent,PlayerInteractActorEvent
import os
from datetime import datetime
import json
import threading
import math
from datetime import datetime, timedelta
import shutil
import time as tm
from collections import defaultdict
import re
import sqlite3
from endstone.form import ModalForm,Dropdown,Label,ActionForm,TextInput,Slider,MessageForm
from endstone.inventory import Inventory,PlayerInventory

# 兼容性代码，用于兼容1.1.3版本之前的数据
def ensure_blockdata_column():
    cursor.execute("PRAGMA table_info(interactions)")
    columns = [column[1] for column in cursor.fetchall()]  # 获取所有列的名称
    if 'blockdata' not in columns:
        cursor.execute("ALTER TABLE interactions ADD COLUMN blockdata TEXT")
        conn.commit()

subdir = "plugins/tianyan_data"
if not os.path.exists(subdir):
    os.makedirs(subdir)
banlist = os.path.join('plugins/tianyan_data/banlist.json')
banidlist = os.path.join('plugins/tianyan_data/banidlist.json')
config_file = os.path.join(subdir, 'config.json')
lang_file = os.path.join(subdir, 'lang.json')
    
# 语言文件操作

default_lang = {
    'lang-version': '1.1.4',
    'language': "中文",
    '是否记录自然方块': '是否记录自然方块',
    '是否记录人工方块': '是否记录人工方块',
    '是否仅记录重要生物': '是否仅记录重要生物',
    '查询玩家&部分实体行为记录 --格式 /ty x坐标 y坐标 z坐标 时间（单位：小时） 半径': '查询玩家&部分实体行为记录 --格式 /ty x坐标 y坐标 z坐标 时间（单位：小时） 半径',
    '查看天眼命令帮助信息': '查看天眼命令帮助信息',
    '封禁一名玩家(仅管理员可用)': '封禁一名玩家(仅管理员可用)',
    '从黑名单中移除玩家(仅管理员可用)': '从黑名单中移除玩家(仅管理员可用)',
    '列出所有加入黑名单的玩家(仅管理员可用)': '列出所有加入黑名单的玩家(仅管理员可用)',
    '封禁设备ID(仅管理员可用)': '封禁设备ID(仅管理员可用)',
    '从设备黑名单移除设备ID(仅管理员可用)': '从设备黑名单移除设备ID(仅管理员可用)',
    '列出所有加入黑名单的设备ID(仅管理员可用)': '列出所有加入黑名单的设备ID(仅管理员可用)',
    '关键词搜索 --格式 /tys 搜索类型  查询关键词 时间（单位：小时） (仅管理员可用)': '关键词搜索 --格式 /tys 搜索类型  查询关键词 时间（单位：小时） (仅管理员可用)',
    '使用图形窗口查询玩家&部分实体行为记录': '使用图形窗口查询玩家&部分实体行为记录',
    '使用图形窗口搜索关键词查询玩家&部分实体行为记录': '使用图形窗口搜索关键词查询玩家&部分实体行为记录',
    '实验性功能 还原玩家直接方块放置破坏行为 --格式 /tyback 坐标 时间（单位：小时） 半径 实施行为的玩家名（可选）（仅管理员可用）': '实验性功能 还原玩家直接方块放置破坏行为 --格式 /tyback 坐标 时间（单位：小时） 半径 实施行为的玩家名（可选）（仅管理员可用）',
    '天眼插件已启用  版本': '天眼插件已启用  版本',
    '配置文件位于': '配置文件位于',
    '插件语言设定为': '插件语言设定为',
    '其余数据文件位于': '其余数据文件位于',
    '项目更新地址': '项目更新地址',
    '天眼命令使用方法': '天眼命令使用方法',
    '使用/tyban 命令将一名玩家加入黑名单 格式 /tyban 玩家名 理由(选填)': '使用/tyban 命令将一名玩家加入黑名单 格式 /tyban 玩家名 理由(选填)',
    '使用/tyunban 命令将一名玩家移出黑名单 格式 /tyunban 玩家名': '使用/tyunban 命令将一名玩家移出黑名单 格式 /tyunban 玩家名',
    '使用/banlist 命令列出所有被加入黑名单的玩家名': '使用/banlist 命令列出所有被加入黑名单的玩家名',
    '使用/banid 命令将一名玩家的设备加入黑名单(当目标玩家设备在线时添加黑名单无法直接踢出，请使用其它方法踢出该玩家) 格式 /banid 设备ID': '使用/banid 命令将一名玩家的设备加入黑名单(当目标玩家设备在线时添加黑名单无法直接踢出，请使用其它方法踢出该玩家) 格式 /banid 设备ID',
    '使用/unbanid 命令将一名玩家的设备移出黑名单 格式 /unban 设备ID': '使用/unbanid 命令将一名玩家的设备移出黑名单 格式 /unban 设备ID',
    '使用/banlist 命令列出所有被加入黑名单的玩家的设备ID': '使用/banlist 命令列出所有被加入黑名单的玩家的设备ID',
    '使用 /ty 命令查询查询玩家&部分实体行为记录 格式 /ty x坐标 y坐标 z坐标 时间（单位：小时） 半径': '使用 /ty 命令查询查询玩家&部分实体行为记录 格式 /ty x坐标 y坐标 z坐标 时间（单位：小时） 半径',
    '使用 /tys 命令使用关键词查询玩家&部分实体行为记录 格式 关键词搜索 格式 /tys 搜索类型  查询关键词 时间（单位：小时） (仅管理员可用)': '使用 /tys 命令使用关键词查询玩家&部分实体行为记录 格式 关键词搜索 格式 /tys 搜索类型  查询关键词 时间（单位：小时） (仅管理员可用)',
    '使用/tygui 命令使用图形窗口查询玩家&部分实体行为记录': '使用/tygui 命令使用图形窗口查询玩家&部分实体行为记录',
    '使用/tysgui 命令使用图形窗口搜索关键词查询玩家&部分实体行为记录 (仅管理员可用)': '使用/tysgui 命令使用图形窗口搜索关键词查询玩家&部分实体行为记录 (仅管理员可用)',
    'tys命令参数解析 搜索类型:player action object(玩家或行为实施者 行为 被实施行为的对象) 搜索关键词:玩家名或行为实施者名 交互 破坏 攻击 放置 被实施行为的对象名': 'tys命令参数解析 搜索类型:player action object(玩家或行为实施者 行为 被实施行为的对象) 搜索关键词:玩家名或行为实施者名 交互 破坏 攻击 放置 被实施行为的对象名',
    '实验性功能 使用/tyback 命令还原玩家直接方块放置破坏行为 格式 /tyback 坐标 时间（单位：小时） 半径 实施行为的玩家名（可选）（仅管理员可用）': '实验性功能 使用/tyback 命令还原玩家直接方块放置破坏行为 格式 /tyback 坐标 时间（单位：小时） 半径 实施行为的玩家名（可选）（仅管理员可用）',
    '命令格式错误！请检查命令是否正确；如果使用~ ~ ~，请直接输入坐标': '命令格式错误！请检查命令是否正确；如果使用~ ~ ~，请直接输入坐标',
    '查询半径最大值为100 !': '查询半径最大值为100 !',
    '未查询到任何结果。': '未查询到任何结果。',
    '已为您查询到此坐标半径': '已为您查询到此坐标半径',
    '格': '格',
    '小时内的玩家&部分实体行为记录': '小时内的玩家&部分实体行为记录',
    '请通过弹窗查看': '请通过弹窗查看',
    '行为实施者': '行为实施者',
    '行为': '行为',
    '坐标': '坐标',
    '时间': '时间',
    '对象类型': '对象类型',
    '维度': '维度',
    '下一页': '下一页',
    '上一页': '上一页',
    '半径': '半径',
    '小时内的查询记录-第': '小时内的查询记录-第',
    '页': '页',
    '小时内的查询记录': '小时内的查询记录',
    '格式错误': '格式错误',
    '玩家': '玩家',
    '已经在': '已经在',
    '被添加至黑名单中了，理由是：': '被添加至黑名单中了，理由是：',
    '请勿重复添加': '请勿重复添加',
    '已被加入黑名单，理由': '已被加入黑名单，理由',
    '理由': '理由',
    '黑名单文件不存在，已自动创建': '黑名单文件不存在，已自动创建',
    '已从黑名单中删除': '已从黑名单中删除',
    '不存在于黑名单中': '不存在于黑名单中',
    '黑名单文件不存在': '黑名单文件不存在',
    '黑名单中没有玩家': '黑名单中没有玩家',
    '于': '于',
    '被封禁，理由': '被封禁，理由',
    '设备ID': '设备ID',
    '被添加至设备ID黑名单中了,请勿重复添加': '被添加至设备ID黑名单中了,请勿重复添加',
    '已被加入黑名单': '已被加入黑名单',
    '设备ID黑名单文件不存在,已自动创建': '设备ID黑名单文件不存在,已自动创建',
    '设备黑名单文件不存在': '设备黑名单文件不存在',
    '没有设备在黑名单中': '没有设备在黑名单中',
    '被封禁': '被封禁',
    '命令格式错误！请检查命令是否正确': '命令格式错误！请检查命令是否正确',
    '命令格式错误！未知的参数': '命令格式错误！未知的参数',
    '已为您查询到关键词': '已为您查询到关键词',
    '的以下相关内容': '的以下相关内容',
    '小时内的记录-第': '小时内的记录-第',
    '小时内的记录': '小时内的记录',
    '控制台无法使用该命令': '控制台无法使用该命令',
    '天眼查询菜单': '天眼查询菜单',
    '输入查询坐标': '输入查询坐标',
    '输入查询时间（单位小时）': '输入查询时间（单位小时）',
    '输入查询半径': '输入查询半径',
    '天眼关键词查询菜单': '天眼关键词查询菜单',
    '选择搜索类型(玩家或行为实施者 行为 被实施行为的对象)': '选择搜索类型(玩家或行为实施者 行为 被实施行为的对象)',
    '关键词': '关键词',
    '输入查询关键词': '输入查询关键词',
    '输入查询时间（单位小时）': '输入查询时间（单位小时）',
    '半径最大值为100 !': '半径最大值为100 !',
    '无记录数据': '无记录数据',
    '开始还原': '开始还原',
    '小时内的方块': '小时内的方块',
    '在': '在',
    '箱子': '箱子',
    '陷阱箱': '陷阱箱',
    '木桶': '木桶',
    '末影箱': '末影箱',
    '漏斗': '漏斗',
    '发射器': '发射器',
    '投掷器': '投掷器',
    '拉杆': '拉杆',
    '未激活的红石中继器': '未激活的红石中继器',
    '未激活的红石比较器': '未激活的红石比较器',
    '激活的红石比较器': '激活的红石比较器',
    '激活的红石中继器': '激活的红石中继器',
    '唱片机': '唱片机',
    '音符盒': '音符盒',
    '按钮': '按钮',
    '告示牌': '告示牌',
    '悬挂式告示牌': '悬挂式告示牌',
    '铁砧': '铁砧',
    '熔炉': '熔炉',
    '高炉': '高炉',
    '潜影盒': '潜影盒',
    '使用': '使用',
    '交互': '交互',
    '破坏': '破坏',
    '放置': '放置',
    '攻击': '攻击',
    '你因涉嫌短时间内发送多条命令被ban': '你因涉嫌短时间内发送多条命令被ban',
    '因涉嫌短时间内发送多条命令被ban': '因涉嫌短时间内发送多条命令被ban',
    '你因涉嫌短时间内发送多条消息被ban': '你因涉嫌短时间内发送多条消息被ban',
    '因涉嫌短时间内发送多条消息被ban': '因涉嫌短时间内发送多条消息被ban',
    '你已被封禁，理由': '你已被封禁，理由',
    '被封禁时间': '被封禁时间',
    '处于封禁名单中，已被踢出，封禁理由为': '处于封禁名单中，已被踢出，封禁理由为',
    '你的设备已于': '你的设备已于',
    '被封禁的设备ID': '被封禁的设备ID',
    '试图加入服务器，已被踢出': '试图加入服务器，已被踢出',
    '设备ID': '设备ID',
    '系统名称': '系统名称',
    '加入了游戏': '加入了游戏',
    '物品槽位': '物品槽位',
    '物品名称': '物品名称',
    '数量': '数量',
    '的物品栏': '的物品栏',
    '搜查玩家物品栏 --格式 /tyo 玩家名': '搜查玩家物品栏 --格式 /tyo 玩家名',
    '使用 /tyo 命令查看玩家物品栏 格式 /tyo 玩家名': '使用 /tyo 命令查看玩家物品栏 格式 /tyo 玩家名',
    '命令错误，请检查参数及玩家是否在线': '命令错误，请检查参数及玩家是否在线',
    '此玩家的物品栏里没有东西': '此玩家的物品栏里没有东西'
}

# 创建默认语言文件
if not os.path.exists(lang_file):
    with open(lang_file, 'w', encoding='utf-8') as f:
        json.dump(default_lang, f, ensure_ascii=False, indent=4)
    print(f"{datetime.now().isoformat()}     [Tianyan] 未检测到语言文件，已创建默认语言文件 No language file was detected, and a default language file has been created.")
   

# 读取语言文件
with open(lang_file, 'r', encoding='utf-8') as f:
    lang = json.load(f)
    
# 语言文件完整性检查    
default_key = set(default_lang.keys())
lang_key = set(lang.keys())
if lang_key == default_key:
    print(f"{datetime.now().isoformat()}     [Tianyan] 语言文件检测正常 Language file detection is normal")
# 语言文件不完整
else:
    # 语言版本信息存在时
    lang_version = lang.get("lang-version", None)
    if lang_version:
        # 语言版本相同 但是部分语言缺失
        if lang["lang-version"] == default_lang["lang-version"]:
            print(f"{datetime.now().isoformat()}     [Tianyan] 天眼语言文件部分缺失! 使用默认语言文件 Part of the language file is missing! Using the default language file")
            lang = default_lang
        elif lang["language"] == "中文":
            # 更新默认语言文件
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(default_lang, f, ensure_ascii=False, indent=4)
            print(f"{datetime.now().isoformat()}     [Tianyan] 天眼语言版本不适配! 已为您自动更新语言文件!")
            lang = default_lang
        # 语言版本不同 提示更新语言文件
        else:
            print(f"{datetime.now().isoformat()}     [Tianyan] 天眼语言版本不适配! 使用默认语言文件! 请下载新的语言文件! The language version is incompatible! Using the default language file! Please download the new language file!")
            lang = default_lang
    else:
        # 无语言版本 信息也缺失 使用默认语言
        print(f"{datetime.now().isoformat()}     [Tianyan] 天眼语言文件部分缺失! 使用默认语言文件! 请下载新的语言文件! Part of the language file is missing! Using the default language file! Please download the new language file!")
        lang = default_lang
    

    
# 根据语言文件中的语言选项加载语言文件 
language = lang.get('language') # 默认语言为中文 


# 配置文件部分
default_config = {
    lang['是否记录自然方块']: True,
    lang['是否记录人工方块']: True,
    lang['是否仅记录重要生物']: True,
}

# 配置文件不存在则创建默认配置文件
if not os.path.exists(config_file):
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)

# 读取配置文件
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

    
# 根据配置文件中的值设置变量
natural = 1 if config.get(lang['是否记录自然方块'], True) else 0
human = 1 if config.get(lang['是否记录人工方块'], True) else 0
nbanimal = 1 if config.get(lang['是否仅记录重要生物'], True) else 0

# 开启自然方块记录不开启人工方块记录
if natural == 1 and human == 0:
    blockrec = 1
# 全开
elif natural == 1 and human == 1:
    blockrec = 2
# 方块全关
elif natural == 0 and human == 0:
    blockrec = 3
# 关闭自然方块记录开启人工方块记录
elif natural == 0 and human == 1:
    blockrec = 4

# 初始化 SQLite 数据库
db_file = "plugins/tianyan_data/tydata.db"
#conn = sqlite3.connect(db_file, check_same_thread=False)
#cursor = conn.cursor()
with sqlite3.connect(db_file, check_same_thread=False) as conn:
    cursor = conn.cursor()
    # 创建表格代码


# 创建表格
cursor.execute("""
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    action TEXT,
    x INTEGER,
    y INTEGER,
    z INTEGER,
    type TEXT,
    world TEXT,
    time TEXT,
    blockdata TEXT
)
""")
conn.commit()

chestrec_data = []
breakrec_data = []
animalrec_data = []
placerec_data = []
actorrec_data = []
lock = threading.Lock()  # 用于线程安全的锁
running_lock = threading.Lock()
is_running = False

# 写入数据的方法
def insert_records(data_list, cursor, has_blockdata=False):
    with sqlite3.connect(db_file) as conn: 
        cursor = conn.cursor()
    with conn:
        for data in data_list:
            if has_blockdata and 'blockdata' in data:
                cursor.execute("""
                    INSERT INTO interactions (name, action, x, y, z, type, world, time, blockdata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['name'], data['action'], data['coordinates']['x'], data['coordinates']['y'],
                      data['coordinates']['z'], data['type'], data['world'], data['time'], data['blockdata']))
            else:
                cursor.execute("""
                    INSERT INTO interactions (name, action, x, y, z, type, world, time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['name'], data['action'], data['coordinates']['x'], data['coordinates']['y'],
                      data['coordinates']['z'], data['type'], data['world'], data['time']))
    data_list.clear()

# 写入数据到 SQLite
def write_to_db():
    global chestrec_data, breakrec_data, animalrec_data, placerec_data, actorrec_data, is_running
    with lock:
        with running_lock:
            if is_running:
                return
            is_running = True

    try:
        
        if placerec_data:
            insert_records(placerec_data, cursor)
        if chestrec_data:
            insert_records(chestrec_data, cursor)
        if breakrec_data:
            insert_records(breakrec_data, cursor, has_blockdata=True)
        if animalrec_data:
            insert_records(animalrec_data, cursor)
        if actorrec_data:
            insert_records(actorrec_data, cursor)
    finally:
        with running_lock:
            is_running = False


# 定期写入数据
def periodic_write():
    while True:
        write_to_db()
        tm.sleep(20)

# 启动线程定期写入
thread = threading.Thread(target=periodic_write)
thread.daemon = True
thread.start()

# 关闭插件时写入文件
def on_plugin_close():
    write_to_db()  # 确保在关闭时写入文件


 
           

class TianyanPlugin(Plugin):
    api_version = "0.5"

    commands = {
        "ty": {
            "description": lang["查询玩家&部分实体行为记录 --格式 /ty x坐标 y坐标 z坐标 时间（单位：小时） 半径"],
            "usages": ["/ty [pos:pos] [float:float] [float:float]"],
            "permissions": ["tianyan_plugin.command.ty"],
        },
        "tyhelp": {
            "description": lang["查看天眼命令帮助信息"],
            "usages": ["/tyhelp"],
            "permissions": ["tianyan_plugin.command.tyhelp"],
        },
        "tyban": {
            "description": lang["封禁一名玩家(仅管理员可用)"],
            "usages": ["/tyban <msg: message> [msg: message]"],
            "permissions": ["tianyan_plugin.command.tyban"],
        },
        "tyunban": {
            "description": lang["从黑名单中移除玩家(仅管理员可用)"],
            "usages": ["/tyunban <msg: message> [msg: message]"],
            "permissions": ["tianyan_plugin.command.tyunban"],
        },
        "tybanlist": {
            "description": lang["列出所有加入黑名单的玩家(仅管理员可用)"],
            "usages": ["/tybanlist"],
            "permissions": ["tianyan_plugin.command.tybanlist"],
        },
        "banid": {
            "description": lang["封禁设备ID(仅管理员可用)"],
            "usages": ["/banid <msg: message>"],
            "permissions": ["tianyan_plugin.command.banid"],
        },
        "unbanid": {
            "description": lang["从设备黑名单移除设备ID(仅管理员可用)"],
            "usages": ["/unbanid <msg: message>"],
            "permissions": ["tianyan_plugin.command.unbanid"],
        },
        "banidlist": {
            "description": lang["列出所有加入黑名单的设备ID(仅管理员可用)"],
            "usages": ["/banidlist"],
            "permissions": ["tianyan_plugin.command.banidlist"],
        },
        "tys": {
            "description": lang["关键词搜索 --格式 /tys 搜索类型  查询关键词 时间（单位：小时） (仅管理员可用)"],
            "usages": ["/tys <msg: message> <msg: message> <float:float>"],
            "permissions": ["tianyan_plugin.command.tys"],
        },
        "tygui": {
            "description": lang["使用图形窗口查询玩家&部分实体行为记录"],
            "usages": ["/tygui"],
            "permissions": ["tianyan_plugin.command.tygui"],
        },
        "tysgui": {
            "description": lang["使用图形窗口搜索关键词查询玩家&部分实体行为记录"],
            "usages": ["/tysgui"],
            "permissions": ["tianyan_plugin.command.tysgui"],
        },
        "tyback": {
            "description": lang["实验性功能 还原玩家直接方块放置破坏行为 --格式 /tyback 坐标 时间（单位：小时） 半径 实施行为的玩家名（可选）（仅管理员可用）"],
            "usages": ["/tyback [pos:pos] <float:float> <float:float> [msg: message]"],
            "permissions": ["tianyan_plugin.command.tyback"],
        },
        "tyo": {
            "description": lang["搜查玩家物品栏 --格式 /tyo 玩家名"],
            "usages": ["/tyo <msg:message>"],
            "permissions": ["tianyan_plugin.command.tyo"],
        }
        #"test": {
        #    "description": "2",
        #    "usages": ["/test"],
        #    "permissions": ["tianyan_plugin.command.test"],
        #},
    }

    permissions = {
        "tianyan_plugin.command.ty": {
            "description": "查询玩家&部分实体行为记录",
            "default": True, 
        },
        "tianyan_plugin.command.tyban": {
            "description": "ban一名玩家",
            "default": "op", 
        },
        "tianyan_plugin.command.tyunban": {
            "description": "从黑名单中移除玩家(仅管理员可用)",
            "default": "op", 
        },
        "tianyan_plugin.command.tybanlist": {
            "description": "列出所有被封禁的玩家(仅管理员可用)",
            "default": "op", 
        },
        "tianyan_plugin.command.banid": {
            "description": "封禁设备ID(仅管理员可用)",
            "default": "op", 
        },
        "tianyan_plugin.command.unbanid": {
            "description": "解除封禁设备ID(仅管理员可用)",
            "default": "op", 
        },
        "tianyan_plugin.command.banidlist": {
            "description": "列出所有被封禁的设备ID(仅管理员可用)",
            "default": "op", 
        },
        "tianyan_plugin.command.tys": {
            "description": "关键词搜索(仅管理员可用)",
            "default": "op", 
        },
        "tianyan_plugin.command.tyhelp": {
            "description": "查看天眼命令帮助信息",
            "default": True, 
        },
        "tianyan_plugin.command.tygui": {
            "description": "使用图形窗口查询玩家&部分实体行为记录",
            "default": True, 
        },
        "tianyan_plugin.command.tysgui": {
            "description": "使用图形窗口搜索关键词查询玩家&部分实体行为记录(仅管理员可用)",
            "default": "op", 
        },
        "tianyan_plugin.command.tyo": {
            "description": "搜查玩家物品栏",
            "default": "op", 
        },
        "tianyan_plugin.command.tyback": {
            "description": "设置回档",
            "default": "op", 
        },
        "tianyan_plugin.command.test": {
            "description": "1",
            "default": True, 
        }
    }

    def on_load(self) -> None:
        self.logger.info("on_load is called!")
        ensure_blockdata_column()

    def on_enable(self) -> None:
        self.logger.info(f"{ColorFormat.YELLOW}{lang["天眼插件已启用  版本"]} V1.1.4.1")
        self.logger.info(f"{ColorFormat.YELLOW}{lang["配置文件位于"]}plugins/tianyan_data/config.json")
        self.logger.info(f"{ColorFormat.YELLOW}{lang["插件语言设定为"]} {language}")
        self.logger.info(f"{ColorFormat.YELLOW}{lang["其余数据文件位于"]} plugins/tianyan_data/")
        self.logger.info(f"{ColorFormat.YELLOW}{lang["项目更新地址"]} https://github.com/yuhangle/Endstone_TianyanPlugin")
        # 监听事件
        self.register_events(self)

    def on_disable(self) -> None:
        self.logger.info("on_disable is called!")
        on_plugin_close()
           
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
                        
        if command.name == "tyhelp":
            sender.send_message(f"{ColorFormat.YELLOW}{lang["天眼命令使用方法"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用/tyban 命令将一名玩家加入黑名单 格式 /tyban 玩家名 理由(选填)"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用/tyunban 命令将一名玩家移出黑名单 格式 /tyunban 玩家名"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用/banlist 命令列出所有被加入黑名单的玩家名"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用/banid 命令将一名玩家的设备加入黑名单(当目标玩家设备在线时添加黑名单无法直接踢出，请使用其它方法踢出该玩家) 格式 /banid 设备ID"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用/unbanid 命令将一名玩家的设备移出黑名单 格式 /unban 设备ID"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用/banlist 命令列出所有被加入黑名单的玩家的设备ID"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用 /ty 命令查询查询玩家&部分实体行为记录 格式 /ty x坐标 y坐标 z坐标 时间（单位：小时） 半径"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用 /tys 命令使用关键词查询玩家&部分实体行为记录 格式 关键词搜索 格式 /tys 搜索类型  查询关键词 时间（单位：小时） (仅管理员可用)"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用/tygui 命令使用图形窗口查询玩家&部分实体行为记录"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用/tysgui 命令使用图形窗口搜索关键词查询玩家&部分实体行为记录 (仅管理员可用)"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["tys命令参数解析 搜索类型:player action object(玩家或行为实施者 行为 被实施行为的对象) 搜索关键词:玩家名或行为实施者名 交互 破坏 攻击 放置 被实施行为的对象名"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["使用 /tyo 命令查看玩家物品栏 格式 /tyo 玩家名"]}")
            sender.send_message(f"{ColorFormat.YELLOW}{lang["实验性功能 使用/tyback 命令还原玩家直接方块放置破坏行为 格式 /tyback 坐标 时间（单位：小时） 半径 实施行为的玩家名（可选）（仅管理员可用）"]}")
            
        elif command.name == "ty":
            if len(args) <= 2:
                if not isinstance(sender, Player):
                    self.logger.info(f"{ColorFormat.RED}{lang["命令格式错误！请检查命令是否正确；如果使用~ ~ ~，请直接输入坐标"]}")
                else:
                    sender.send_error_message(lang["命令格式错误！请检查命令是否正确；如果使用~ ~ ~，请直接输入坐标"])
                return True
            elif "~" in args[0]:
                if not isinstance(sender, Player):
                    self.logger.info(f"{ColorFormat.RED}{lang["命令格式错误！请检查命令是否正确；如果使用~ ~ ~，请直接输入坐标"]}")
                else:
                    sender.send_error_message(lang["命令格式错误！请检查命令是否正确；如果使用~ ~ ~，请直接输入坐标"])
            elif float(args[2]) > 100:
                if not isinstance(sender, Player):
                    self.logger.info(f"{ColorFormat.RED}{lang["查询半径最大值为100 !"]}")
                else:
                    sender.send_error_message(lang["查询半径最大值为100 !"])
            else:
                positions = args[0]
                times = float(args[1])
                r = float(args[2])
                coordinates = positions
                x, y, z = map(float, coordinates.split())
                max_lines = 322
                
                # 获取当前时间
                current_time = datetime.now()
                time_threshold = current_time - timedelta(hours=times)
                
                # 查询数据库
                results = []
                query = """
                SELECT name, action, x, y, z, type, world, time FROM interactions
                WHERE (x - ?)*(x - ?) + (y - ?)*(y - ?) + (z - ?)*(z - ?) <= ?
                AND time >= ?
                """
                radius_squared = r ** 2
                with conn:
                    cursor.execute(query, (x, x, y, y, z, z, radius_squared, time_threshold.isoformat()))
                    rows = cursor.fetchall()
                    for row in rows:
                        results.append({
                            'name': row[0],
                            'action': row[1],
                            'coordinates': {'x': row[2], 'y': row[3], 'z': row[4]},
                            'type': row[5],
                            'world': row[6],
                            'time': row[7]
                        })
                
                # 处理结果
                if not results:
                    if not isinstance(sender, Player):
                        self.logger.info(f"{ColorFormat.YELLOW}{lang["未查询到任何结果。"]}")
                    else:
                        sender.send_message(f"{ColorFormat.YELLOW}{lang["未查询到任何结果。"]}")
                else:
                    if not isinstance(sender, Player):
                        self.logger.info(f"{ColorFormat.YELLOW}{lang["已为您查询到此坐标半径"]}{r}{lang["格"]}{times}{lang["小时内的玩家&部分实体行为记录"]}")
                    else:
                        sender.send_message(f"{ColorFormat.YELLOW}{lang["已为您查询到此坐标半径"]}{r}{lang["格"]}{times}{lang["小时内的玩家&部分实体行为记录"]}，{lang["请通过弹窗查看"]}")
                    output_message = ""  # 创建一个空字符串用于存储所有输出信息
                    for item in results:
                        name = item['name']
                        coordinates = item['coordinates']
                        type = item['type']
                        time = item['time']
                        world = item['world']
                        action = item['action']
                        
                        # 格式化单条记录的信息
                        message = f"{ColorFormat.YELLOW} {lang["行为实施者"]}: {name} \n {lang["行为"]}: {action} \n {lang["坐标"]}: {coordinates} \n {lang["时间"]}: {time} \n {lang["对象类型"]}: {type} \n {lang["维度"]}: {world}\n"
                        output_message += message + "-" * 20 + "\n"  # 将单条记录添加到总输出中                  
                    if not isinstance(sender, Player):
                        self.logger.info(output_message)
                    else:
                        #self.server.get_player(sender.name).send_form(ActionForm(title=f'{ColorFormat.BLUE}§l§o半径{r}格{times}小时内的查询记录',content=output_message))
                        lines = output_message.split("\n")
                        if len(lines) > max_lines:
                            page = 0
                            segments = ["\n".join(lines[i:i + max_lines]) for i in range(0, len(lines), max_lines)]
                            
                            def show(sender):
                                
                                def next_button_click():
                                    def on_click(sender):
                                        nonlocal page  # 使用 nonlocal 声明 page 是外部作用域的变量
                                        page += 1
                                        if page >= len(segments):  # 判断是否还有下一页
                                            page = 0  # 回到第一页
                                        show(sender)
                                    return on_click
                                
                                def up_button_click():
                                    def on_click(sender):
                                        nonlocal page  # 使用 nonlocal 声明 page 是外部作用域的变量
                                        if page == 0:  # 如果在第一页，跳转到最后一页
                                            page = len(segments) - 1
                                        else:
                                            page -= 1
                                        show(sender)
                                    return on_click
                                
                                next =  ActionForm.Button(text=f"{lang["下一页"]}",on_click=next_button_click())
                                up =  ActionForm.Button(text=f"{lang["上一页"]}",on_click=up_button_click())
                                    
                            # 显示第一页窗口
                                self.server.get_player(sender.name).send_form(
                                    ActionForm(
                                        title=f'{ColorFormat.BLUE}§l§o{lang["半径"]}{r}{lang["格"]}{times}{lang["小时内的查询记录-第"]}{page + 1}{lang["页"]}',
                                        content=segments[page],
                                        buttons=[up,next]
                                        )
                                    )
                            show(sender)
                        else:
                            self.server.get_player(sender.name).send_form(
                                    ActionForm(
                                        title=f'{ColorFormat.BLUE}§l§o{lang["半径"]}{r}{lang["格"]}{times}{lang["小时内的查询记录"]}',
                                        content=output_message,
                                        )
                                    )
                        
        elif command.name == "tyban":
            if len(args) == 0:
                if not isinstance(sender, Player):
                    self.logger.info(lang["格式错误"])
                else:
                    sender.send_error_message(lang["格式错误"])
            if len(args) >= 3:
                if not isinstance(sender, Player):
                    self.logger.info(lang["格式错误"])
                else:
                    sender.send_error_message(lang["格式错误"])
            else:
                if len(args) == 2:
                    playername = args[0]
                    reason = args[1]
                if len(args) == 1:
                    playername = args[0]
                    reason = "No reason"

                # 检查文件是否存在
                if not os.path.exists(banlist):
                    # 如果文件不存在，创建一个空的黑名单文件
                    with open(banlist, 'w') as file:
                        json.dump({}, file)

                # 读取黑名单文件
                with open(banlist, 'r',encoding='utf-8') as file:
                    blacklist = json.load(file)
                    
                if playername in blacklist:
                    if not isinstance(sender, Player):
                        entry = blacklist[playername]
                        reason = entry.get("reason")
                        timestamp = entry.get("timestamp")
                        self.logger.info(f"{lang["玩家"]} {playername} {lang["已经在"]}{timestamp}{lang["被添加至黑名单中了，理由是："]}{reason}，{lang["请勿重复添加"]}")
                    else:
                        reason = blacklist[playername]
                        sender.send_message(f"{lang["玩家"]} {playername} {lang["已经在"]}{timestamp}{lang["被添加至黑名单中了，理由是："]}{reason}，{lang["请勿重复添加"]}")
                else:
                    # 将玩家名和理由写入黑名单
                    timestamp = datetime.now().isoformat()  # 使用当前时间戳作为默认值
                    # 创建包含所有信息的新条目
                    entry = {
                        "reason": reason,
                        "timestamp": timestamp
                    }
                    blacklist[playername] = entry

                    # 将更新后的黑名单写回文件
                    with open(banlist, 'w', encoding='utf-8') as file:  # 指定编码为 UTF-8
                        json.dump(blacklist, file, ensure_ascii=False, indent=4)
                    
                    if not isinstance(sender, Player):
                        self.logger.info(f"{lang["玩家"]} {playername} {lang["已被加入黑名单，理由"]}:{reason}")
                        self.server.dispatch_command(self.server.command_sender,f'kick "{playername}" "理由：{reason}"')
                    else:
                        sender.send_message(f"{lang["玩家"]} {playername} {lang["已被加入黑名单，理由"]}:{reason}")
                        sender.perform_command(f'kick "{playername}" "{lang["理由"]}:{reason}"')
        
        elif command.name == "tyunban":
            if len(args) == 0:
                if not isinstance(sender, Player):
                    self.logger.info(lang["格式错误"])
                else:
                    sender.send_error_message(lang["格式错误"])
            if len(args) >= 2:
                if not isinstance(sender, Player):
                    self.logger.info(lang["格式错误"])
                else:
                    sender.send_error_message(lang["格式错误"])
            else:
                yplayername = args[0]
                playername = yplayername.strip('"')
                # 检查文件是否存在
                if not os.path.exists(banlist):
                    # 如果文件不存在，创建一个空的黑名单文件
                    with open(banlist, 'w',encoding='utf-8') as file:
                        json.dump({}, file)
                    if not isinstance(sender, Player):
                        self.logger.info(lang["黑名单文件不存在，已自动创建"])
                    else:
                        sender.send_error_message(lang["黑名单文件不存在，已自动创建"])
                else:
                    # 读取黑名单文件
                    with open(banlist, 'r', encoding='utf-8') as file:
                        blacklist = json.load(file)
                    
                    # 检查玩家是否在黑名单中
                    if playername in blacklist:
                        del blacklist[playername]
                        # 将更新后的黑名单写回文件
                        with open(banlist, 'w', encoding='utf-8') as file:  # 指定编码为 UTF-8
                            json.dump(blacklist, file, ensure_ascii=False, indent=4)
                        if not isinstance(sender, Player):
                            self.logger.info(f"{lang["玩家"]} {playername} {lang["已从黑名单中删除"]}。")
                        else:
                            sender.send_error_message(f"{lang["玩家"]} {playername} {lang["已从黑名单中删除"]}。")
                    else:
                        if not isinstance(sender, Player):
                            self.logger.info(f"{lang["玩家"]} {playername} {lang["不存在于黑名单中"]}。")
                        else:
                            sender.send_error_message(f"{lang["玩家"]} {playername} {lang["不存在于黑名单中"]}。")
        elif command.name == "tybanlist":
            # 检查文件是否存在
            if not os.path.exists(banlist):
                if not isinstance(sender, Player):
                    self.logger.info(lang["黑名单文件不存在"])
                else:
                    sender.send_error_message(lang["黑名单文件不存在"])
                    
            else:
                # 读取黑名单文件
                with open(banlist, 'r', encoding='utf-8') as file:
                    blacklist = json.load(file)
                if not blacklist:
                    if not isinstance(sender, Player):
                        self.logger.info(lang["黑名单中没有玩家"])
                    else:
                        sender.send_error_message(lang["黑名单中没有玩家"])
                else:
                    # 遍历黑名单中的所有玩家
                    for playername, entry in blacklist.items():
                        reason = entry.get("reason")
                        timestamp = entry.get("timestamp")
                        if not isinstance(sender, Player):
                            self.logger.info(f"{lang["玩家"]} {playername} {lang["于"]}{timestamp}{lang["被封禁，理由"]}：{reason}")
                        else:
                            sender.send_error_message(f"{lang["玩家"]} {playername} {lang["于"]}{timestamp}{lang["被封禁，理由"]}：{reason}")

        elif command.name == "banid":
            if len(args) == 0:
                if not isinstance(sender, Player):
                    self.logger.info(lang["格式错误"])
                else:
                    sender.send_error_message(lang["格式错误"])
            if len(args) >= 2:
                if not isinstance(sender, Player):
                    self.logger.info(lang["格式错误"])
                else:
                    sender.send_error_message(lang["格式错误"])
            else:
                if len(args) == 1:
                    device_id = args[0]

                # 检查文件是否存在
                if not os.path.exists(banidlist):
                    # 如果文件不存在，创建一个空的黑名单文件
                    with open(banidlist, 'w') as file:
                        json.dump({}, file)

                # 读取设备id黑名单文件
                with open(banidlist, 'r',encoding='utf-8') as file:
                    blackidlist = json.load(file)
                    
                if device_id in blackidlist:
                    if not isinstance(sender, Player):
                        entry = blackidlist[device_id]
                        timestamp = entry.get("timestamp")
                        self.logger.info(f"{lang["设备ID"]} {device_id} {lang["已经在"]}{timestamp}{lang["被添加至设备ID黑名单中了,请勿重复添加"]}")
                    else:
                        entry = blackidlist[device_id]
                        timestamp = entry.get("timestamp")
                        sender.send_error_message(f"{lang["设备ID"]} {device_id} {lang["已经在"]}{timestamp}{lang["被添加至设备ID黑名单中了,请勿重复添加"]}")
                else:
                    # 将设备id写入黑名单
                    timestamp = datetime.now().isoformat()  # 使用当前时间戳作为默认值
                    # 创建包含所有信息的新条目
                    entry = {
                        "timestamp": timestamp
                    }
                    blackidlist[device_id] = entry

                    # 将更新后的黑名单写回文件
                    with open(banidlist, 'w', encoding='utf-8') as file:  # 指定编码为 UTF-8
                        json.dump(blackidlist, file, ensure_ascii=False, indent=4)
                    if not isinstance(sender, Player):
                        self.logger.info(f"{lang["设备ID"]} {device_id} {lang["已被加入黑名单"]}")
                    else:
                        sender.send_error_message(f"{lang["设备ID"]} {device_id} {lang["已被加入黑名单"]}")
        
        elif command.name == "unbanid":
            if len(args) == 0:
                if not isinstance(sender, Player):
                    self.logger.info(lang["格式错误"])
                else:
                    sender.send_error_message(lang["格式错误"])
            if len(args) >= 2:
                if not isinstance(sender, Player):
                    self.logger.info(lang["格式错误"])
                else:
                    sender.send_error_message(lang["格式错误"])
            else:
                device_id = args[0]
                # 检查文件是否存在
                if not os.path.exists(banlist):
                    # 如果文件不存在，创建一个空的黑名单文件
                    with open(banidlist, 'w',encoding='utf-8') as file:
                        json.dump({}, file)
                    if not isinstance(sender, Player):
                        self.logger.info(lang["设备ID黑名单文件不存在,已自动创建"])
                    else:
                        sender.send_error_message(lang["设备ID黑名单文件不存在,已自动创建"])
                else:
                    # 读取设备黑名单文件
                    with open(banidlist, 'r', encoding='utf-8') as file:
                        blackidlist = json.load(file)
                    
                    # 检查设备是否在黑名单中
                    if device_id in blackidlist:
                        del blackidlist[device_id]
                        # 将更新后的黑名单写回文件
                        with open(banidlist, 'w', encoding='utf-8') as file:  # 指定编码为 UTF-8
                            json.dump(blackidlist, file, ensure_ascii=False, indent=4)
                        if not isinstance(sender, Player):
                            self.logger.info(f"{lang["设备ID"]} {device_id} {lang["已从黑名单中删除"]}")
                        else:
                            sender.send_message(f"{lang["设备ID"]} {device_id} {lang["已从黑名单中删除"]}")
                    else:
                        if not isinstance(sender, Player):
                            self.logger.info(f"{lang["设备ID"]} {device_id} {lang["不存在于黑名单中"]}")
                        else:
                            sender.send_error_message(f"{lang["设备ID"]} {device_id} {lang["不存在于黑名单中"]}")
                            
        elif command.name == "banidlist":
            # 检查文件是否存在
            if not os.path.exists(banidlist):
                if not isinstance(sender, Player):
                    self.logger.info(lang["设备黑名单文件不存在"])
                else:
                    sender.send_error_message(lang["设备黑名单文件不存在"])
                    
            else:
                # 读取设备黑名单文件
                with open(banidlist, 'r', encoding='utf-8') as file:
                    blackidlist = json.load(file)
                if not blackidlist:
                    if not isinstance(sender, Player):
                        self.logger.info(lang["没有设备在黑名单中"])
                    else:
                        sender.send_error_message(lang["没有设备在黑名单中"])
                else:
                    # 遍历黑名单中的所有设备
                    for device_id, entry in blackidlist.items():
                        timestamp = entry.get("timestamp")
                        if not isinstance(sender, Player):
                            self.logger.info(f"{lang["设备ID"]} {device_id} {lang["于"]}{timestamp}{lang["被封禁"]}")
                        else:
                            sender.send_message(f"{lang["设备ID"]} {device_id} {lang["于"]}{timestamp}{lang["被封禁"]}")
        elif command.name == "tys":
            if len(args) <= 2:
                if not isinstance(sender, Player):
                    self.logger.info(f"{ColorFormat.RED}{lang["命令格式错误！请检查命令是否正确"]}")
                else:
                    sender.send_error_message(lang["命令格式错误！请检查命令是否正确"])
                return True
            elif args[0] not in ["player", "action", "object"]:  # 玩家、行为、对象
                if not isinstance(sender, Player):
                    self.logger.info(f"{ColorFormat.RED}{lang["命令格式错误！未知的参数"]} {args[0]}")
                else:
                    sender.send_error_message(f"{lang["命令格式错误！未知的参数"]} {args[0]}")
            else:
                searchtype = args[0]  # 搜索类型
                searchobject = args[1]  # 搜索关键词
                time = float(args[2])  # 搜索时间范围
                # 最大行数限制
                max_lines = 322
                            
                def search_db(keyword, time, stype):
                    """
                    从 SQLite 数据库中查询符合条件的记录。

                    Args:
                        keyword: 搜索关键词
                        time: 时间范围（单位：小时）
                        stype: 搜索字段类型

                    Returns:
                        符合条件的记录列表
                    """
                    now = datetime.now()
                    search_time = now - timedelta(hours=time)

                    query = f"""
                    SELECT name, action, x, y, z, type, world, time 
                    FROM interactions
                    WHERE {stype} LIKE ?
                    AND time >= ?
                    """
                    results = []
                    with conn:
                        cursor.execute(query, (f"%{keyword}%", search_time.isoformat()))
                        rows = cursor.fetchall()
                        for row in rows:
                            results.append({
                                'name': row[0],
                                'action': row[1],
                                'coordinates': {'x': row[2], 'y': row[3], 'z': row[4]},
                                'type': row[5],
                                'world': row[6],
                                'time': row[7]
                            })
                    return results

                def output(keyword, time, stype):
                    results = search_db(keyword, time, stype)
                    if not results:
                        if not isinstance(sender, Player):
                            self.logger.info(f"{ColorFormat.YELLOW}{lang["未查询到任何结果。"]}")
                        else:
                            sender.send_message(f"{ColorFormat.YELLOW}{lang["未查询到任何结果。"]}")
                    else:
                        if not isinstance(sender, Player):
                            self.logger.info(f"{ColorFormat.YELLOW}\n{lang["已为您查询到关键词"]} {keyword} {lang["的以下相关内容"]}" + "-" * 20)
                        else:
                            sender.send_message(f"{ColorFormat.YELLOW}{lang["已为您查询到关键词"]} {keyword} {lang["的以下相关内容"]},{lang["请通过弹窗查看"]}\n")
                        output_message = ""  # 创建一个空字符串用于存储所有输出信息
                        for record in results:
                        # 格式化单条记录的信息
                            message = f" {ColorFormat.YELLOW}{lang["行为实施者"]}: {record['name']} \n {lang["行为"]}: {record['action']} \n {lang["坐标"]}: {record['coordinates']} \n {lang["时间"]}: {record['time']} \n {lang["对象类型"]}: {record['type']} \n {lang["维度"]}: {record['world']}\n"
                            output_message += message + "-" * 20 + "\n"  # 将单条记录添加到总输出中   
                        if not isinstance(sender, Player):
                            self.logger.info(output_message)
                        else:
                            lines = output_message.split("\n")
                            if len(lines) > max_lines:
                                page = 0
                                segments = ["\n".join(lines[i:i + max_lines]) for i in range(0, len(lines), max_lines)]
                                
                                def show(sender):
                                    
                                    def next_button_click():
                                        def on_click(sender):
                                            nonlocal page  # 使用 nonlocal 声明 page 是外部作用域的变量
                                            page += 1
                                            if page >= len(segments):  # 判断是否还有下一页
                                                page = 0  # 回到第一页
                                            show(sender)
                                        return on_click
                                    
                                    def up_button_click():
                                        def on_click(sender):
                                            nonlocal page  # 使用 nonlocal 声明 page 是外部作用域的变量
                                            if page == 0:  # 如果在第一页，跳转到最后一页
                                                page = len(segments) - 1
                                            else:
                                                page -= 1
                                            show(sender)
                                        return on_click
                                    
                                    next =  ActionForm.Button(text=f"{lang["下一页"]}",on_click=next_button_click())
                                    up =  ActionForm.Button(text=f"{lang["上一页"]}",on_click=up_button_click())
                                        
                                # 显示第一页窗口
                                    self.server.get_player(sender.name).send_form(
                                        ActionForm(
                                            title=f'{ColorFormat.BLUE}§l§o{keyword} {lang["在"]} {time} {lang["小时内的记录-第"]} {page + 1} {lang["页"]}',
                                            content=segments[page],
                                            buttons=[up,next]
                                            )
                                        )
                                show(sender)
                            else:
                                self.server.get_player(sender.name).send_form(
                                        ActionForm(
                                            title=f'{ColorFormat.BLUE}§l§o{keyword} {lang["在"]} {time} {lang["小时内的记录"]}',
                                            content=output_message,
                                            )
                                        )

                # 玩家名搜索
                if searchtype == "player":
                    stype = "name"
                    keyword = searchobject
                    output(keyword, time, stype)
                # 行为搜索
                elif searchtype == "action":
                    stype = "action"
                    keyword = searchobject
                    output(keyword, time, stype)
                # 对象目标搜索
                elif searchtype == "object":
                    stype = "type"
                    keyword = searchobject
                    output(keyword, time, stype)
                    
        elif command.name == "tygui":
            if not isinstance(sender, Player):
                sender.send_error_message(lang["控制台无法使用该命令"])
            else:
                submit = lambda player, json_str: (
                    #self.logger.info(f"Received JSON: {json_str}"),  # 记录日志
                    player.perform_command(
                        f'ty {__import__("json").loads(json_str)[0]} {__import__("json").loads(json_str)[1]} {__import__("json").loads(json_str)[2]}'
                    )
                )
                self.server.get_player(sender.name).send_form(
                    ModalForm(
                        title=f'{ColorFormat.YELLOW}{lang["天眼查询菜单"]}',
                        controls=[
                            TextInput(label= lang["坐标"], placeholder= lang['输入查询坐标']),
                            TextInput(label= lang['时间'], placeholder= lang['输入查询时间（单位小时）']),
                            TextInput(label= lang['半径'], placeholder= lang['输入查询半径'])
                        ],
                        on_submit=submit
                    )
                )
            
        elif command.name == "tysgui":
            if not isinstance(sender, Player):
                sender.send_error_message(lang["控制台无法使用该命令"])
            else:
                submit = lambda player, json_str: (
                    #self.logger.info(f"Received JSON: {json_str}"),  # 记录日志
                    player.perform_command(
                        f'tys {['player','action','object'][__import__('json').loads(json_str)[0]]} "{__import__("json").loads(json_str)[1]}" {__import__("json").loads(json_str)[2]}'
                    )
                )
                self.server.get_player(sender.name).send_form(
                    ModalForm(
                        title=f'{ColorFormat.YELLOW}{lang["天眼关键词查询菜单"]}',
                        controls=[
                            Dropdown(label= lang['选择搜索类型(玩家或行为实施者 行为 被实施行为的对象)'],options=['player','action','object']),
                            TextInput(label= lang['关键词'], placeholder= lang['输入查询关键词']),
                            TextInput(label= lang['时间'], placeholder= lang['输入查询时间（单位小时）']),
                        ],
                        on_submit=submit
                    )
                )
                
        elif command.name == "tyo":
            if len(args) == 1:
                try:
                    playername = args[0]
                    all_item = []
                    for item_num in range(36):
                        item = self.server.get_player(playername).inventory.get_item(item_num)
                        if item:  # 如果槽位不为空
                            item_name = item.type
                            item_amount = item.amount
                            all_item.append({'num': item_num, 'item': item_name, 'amount': item_amount})

                    # 打印所有物品信息
                    output_item = ""
                    for item_info in all_item:
                        message = f"{ColorFormat.YELLOW}{lang["物品槽位"]}:{item_info['num']} \n {lang["物品名称"]}:{item_info['item']} \n {lang["数量"]}:{item_info['amount']}\n"
                        output_item += message + "-" * 20 + "\n"  # 将单条记录添加到总输出中
                    if not isinstance(sender, Player):
                        self.server.logger.info(f"{ColorFormat.YELLOW}\n{output_item}")
                    else:
                        if output_item == "":
                            if not isinstance(sender, Player):
                                self.logger.info(f"{ColorFormat.RED}{lang["此玩家的物品栏里没有东西"]}")
                            else:
                                sender.send_error_message(f"{ColorFormat.RED}{lang["此玩家的物品栏里没有东西"]}")
                        else:
                            self.server.get_player(sender.name).send_form(ActionForm(title=f"§1{playername}{lang["的物品栏"]}",content=output_item))
                except:
                    if not isinstance(sender, Player):
                        self.logger.info(f"{ColorFormat.RED}{lang["命令错误，请检查参数及玩家是否在线"]}")
                    else:
                        sender.send_error_message(f"{ColorFormat.RED}{lang["命令错误，请检查参数及玩家是否在线"]}")
            else:
                pass
            
        elif command.name == "tyback":
            if len(args) < 3:
                if not isinstance(sender, Player):
                    self.logger.info(f"{ColorFormat.RED}{lang["命令格式错误！请检查命令是否正确；如果使用~ ~ ~，请直接输入坐标"]}")
                else:
                    sender.send_error_message(lang["命令格式错误！请检查命令是否正确；如果使用~ ~ ~，请直接输入坐标"])
                return True
            elif "~" in args[0]:
                if not isinstance(sender, Player):
                    self.logger.info(f"{ColorFormat.RED}{lang["命令格式错误！请检查命令是否正确；如果使用~ ~ ~，请直接输入坐标"]}")
                else:
                    sender.send_error_message(lang["命令格式错误！请检查命令是否正确；如果使用~ ~ ~，请直接输入坐标"])
            elif float(args[2]) > 100:
                if not isinstance(sender, Player):
                    self.logger.info(f"{ColorFormat.RED}{lang["半径最大值为100 !"]}")
                else:
                    sender.send_error_message(lang["半径最大值为100 !"])
            else:
                positions = args[0]
                times = float(args[1])
                r = float(args[2])
                coordinates = positions
                x, y, z = map(float, coordinates.split())
                max_lines = 322
                exe_player_dim = self.server.get_player(sender.name).location.dimension.name
                
                # 获取当前时间
                current_time = datetime.now()
                time_threshold = current_time - timedelta(hours=times)
                
                # 对单独玩家行为回档
                if len(args) == 4:
                    do_player_name = args[3]
                
                    # 查询数据库
                    results = []
                    query = """
                    SELECT name, action, x, y, z, type, world, time, blockdata FROM interactions
                    WHERE (x - ?)*(x - ?) + (y - ?)*(y - ?) + (z - ?)*(z - ?) <= ?
                    AND time >= ?
                    AND world = ?
                    AND name = ?
                    """
                    radius_squared = r ** 2
                    with conn:
                        cursor.execute(query, (x, x, y, y, z, z, radius_squared, time_threshold.isoformat(),exe_player_dim,do_player_name))
                        rows = cursor.fetchall()
                        for row in rows:
                            results.append({
                                'name': row[0],
                                'action': row[1],
                                'coordinates': {'x': row[2], 'y': row[3], 'z': row[4]},
                                'type': row[5],
                                'world': row[6],
                                'time': row[7],
                                'blockdata': row[8] if row[8] is not None else ''  # 处理blockdata字段
                            })
                # 没有玩家信息就不加
                else:
                    # 查询数据库
                    results = []
                    query = """
                    SELECT name, action, x, y, z, type, world, time, blockdata FROM interactions
                    WHERE (x - ?)*(x - ?) + (y - ?)*(y - ?) + (z - ?)*(z - ?) <= ?
                    AND time >= ?
                    AND world = ?
                    """
                    radius_squared = r ** 2
                    with conn:
                        cursor.execute(query, (x, x, y, y, z, z, radius_squared, time_threshold.isoformat(),exe_player_dim))
                        rows = cursor.fetchall()
                        for row in rows:
                            results.append({
                                'name': row[0],
                                'action': row[1],
                                'coordinates': {'x': row[2], 'y': row[3], 'z': row[4]},
                                'type': row[5],
                                'world': row[6],
                                'time': row[7],
                                'blockdata': row[8] if row[8] is not None else None  # 处理blockdata字段
                            })
                
                # 处理结果
                if not results:
                    if not isinstance(sender, Player):
                        self.logger.info(f"{ColorFormat.RED}{lang["控制台无法使用该命令"]}")
                    else:
                        sender.send_message(f"{ColorFormat.YELLOW}{lang["无记录数据"]}")
                else:
                    if not isinstance(sender, Player):
                        self.logger.info(f"{ColorFormat.RED}{lang["控制台无法使用该命令"]}")
                    else:
                        sender.send_message(f"{ColorFormat.YELLOW}{lang["开始还原"]}{r}{lang["格"]}{times}{lang["小时内的方块"]}")
                        
                        for item in results:
                            
                            turnaction = item['action']
                            if turnaction == lang['破坏']:
                                coordinates = item['coordinates']
                                type = item['type']
                                x,y,z = coordinates['x'],coordinates['y'],coordinates['z']
                                pos = f'{x} {y} {z}'
                                blockdata = item['blockdata']
                                sender.perform_command(f'setblock {pos} {type}{blockdata}')
                                #action = '放置'
                            elif turnaction == lang['放置']:
                                coordinates = item['coordinates']
                                x,y,z = coordinates['x'],coordinates['y'],coordinates['z']
                                pos = f'{x} {y} {z}'
                                sender.perform_command(f'setblock {pos} air')
                                #action = '破坏'
                        
        
        elif command.name == "test":
            self.server.get_player(sender.name).send_form(
                MessageForm(
                    title='测试表单',
                    content='先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。然侍卫之臣不懈于内，忠志之士忘身于外者，盖追先帝之殊遇，欲报之于陛下也。诚宜开张圣听，以光先帝遗德，恢弘志士之气，不宜妄自菲薄，引喻失义，以塞忠谏之路也。',
                    button1='确定',
                    button2='取消'
                )
            )
        
# 容器交互和其它交互事件
    @event_handler
    def blockjh(self,event: PlayerInteractEvent): 
        # 分割线
        def record_data(name, action, x, y, z, type,world):
            # """记录玩家的交互行为到data.json文件中"""
            interaction = {
                'name': name,
                'action': action,
                'coordinates': {'x': x, 'y': y, 'z': z},
                'time': datetime.now().isoformat(),  # 记录当前时间
                'type': type,
                "world": world
            } 
            
            with lock:  # 确保线程安全
                chestrec_data.append(interaction)                  
            #threading.Thread(target=write_to_file).start()
            
        if event.block.type == "minecraft:chest":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["箱子"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:trapped_chest":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["陷阱箱"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:barrel":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["木桶"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:ender_chest":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["末影箱"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:hopper":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["漏斗"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:dispenser":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["发射器"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:dropper":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["投掷器"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:lever":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["拉杆"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:unpowered_repeater":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["未激活的红石中继器"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:unpowered_comparator":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["未激活的红石比较器"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:powered_comparator":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["激活的红石比较器"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:powered_repeater":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["激活的红石中继器"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:jukebox":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["唱片机"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type == "minecraft:noteblock":
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["音符盒"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type in [
            "minecraft:wooden_button","minecraft:spruce_button","minecraft:birch_button","minecraft:jungle_button","minecraft:acacia_button",
            "minecraft:dark_oak_button","minecraft:mangrove_button","minecraft:cherry_button","minecraft:bamboo_button","minecraft:pale_oak_button",
            "minecraft:crimson_button","minecraft:warped_button","minecraft:stone_button","minecraft:polished_blackstone_button"
            ]:
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["按钮"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type in [
            "minecraft:standing_sign","minecraft:spruce_standing_sign","minecraft:birch_standing_sign","minecraft:jungle_standing_sign","minecraft:acacia_standing_sign",
            "minecraft:darkoak_standing_sign","minecraft:mangrove_standing_sign","minecraft:cherry_standing_sign","minecraft:pale_oak_standing_sign","minecraft:bamboo_standing_sign",
            "minecraft:crimson_standing_sign","minecraft:warped_standing_sign","minecraft:wall_sign","minecraft:spruce_wall_sign","minecraft:birch_wall_sign","minecraft:jungle_wall_sign",
            "minecraft:acacia_wall_sign","minecraft:darkoak_wall_sign","minecraft:mangrove_wall_sign","minecraft:cherry_wall_sign","minecraft:pale_oak_wall_sign","minecraft:bamboo_wall_sign","minecraft:crimson_wall_sign","minecraft:warped_wall_sign"
            ]:
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["告示牌"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type in [
            "minecraft:oak_hanging_sign","minecraft:spruce_hanging_sign","minecraft:birch_hanging_sign","jungle_hanging_sign","acacia_hanging_sign",
            "dark_oak_hanging_sign","mangrove_hanging_sign","cherry_hanging_sign","pale_oak_hanging_sign","bamboo_hanging_sign","crimson_hanging_sign","warped_hanging_sign"
            ]:
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["悬挂式告示牌"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type in [
            "minecraft:anvil","minecraft:chipped_anvil","minecraft:damaged_anvil"
            ]:
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["铁砧"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type in [
            "minecraft:furnace","minecraft:lit_furnace"
            ]:
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["熔炉"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
            
        if event.block.type in [
            "minecraft:blast_furnace","minecraft:lit_blast_furnace"
            ]:
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = lang["高炉"]
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type, world)
        
        if event.block.type in [
            "minecraft:undyed_shulker_box", "minecraft:white_shulker_box", 
            "minecraft:light_gray_shulker_box", "minecraft:gray_shulker_box", 
            "minecraft:brown_shulker_box", "minecraft:red_shulker_box", 
            "minecraft:orange_shulker_box", "minecraft:yellow_shulker_box", 
            "minecraft:lime_shulker_box", "minecraft:green_shulker_box", 
            "minecraft:cyan_shulker_box", "minecraft:light_blue_shulker_box", 
            "minecraft:blue_shulker_box", "minecraft:purple_shulker_box", 
            "minecraft:magenta_shulker_box", "minecraft:pink_shulker_box"
        ]:
            name = event.player.name
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            world = event.block.location.dimension.name
            type = lang["潜影盒"]
            record_data(name, action, x, y, z, type,world)
        
        if str(event.item) in [
            "ItemStack(minecraft:flint_and_steel x 1)","ItemStack(minecraft:lava_bucket x 1)","ItemStack(minecraft:water_bucket x 1)","ItemStack(minecraft:powder_snow_bucket x 1)","ItemStack(minecraft:cod_bucket x 1)","ItemStack(minecraft:salmon_bucket x 1)","ItemStack(minecraft:pufferfish_bucket x 1)","ItemStack(minecraft:tropical_fish_bucket x 1)","ItemStack(minecraft:axolotl_bucket x 1)","ItemStack(minecraft:tadpole_bucket x 1)"
        ]:
            name = event.player.name
            blocktype = event.block.type
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = f"{blocktype}，{lang["使用"]}{event.item}"
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type,world)
            
        # 数量未定
        item_str = str(event.item)
        bucket_pattern = r"ItemStack\(minecraft:bucket\s+x\s*\d+\)"
        if re.match(bucket_pattern, item_str) and event.block.type in [
            "minecraft:water","minecraft:lava","minecraft:powder_snow"]:# 桶对可被桶装的方块交互
            name = event.player.name
            blocktype = event.block.type
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = f"{blocktype}，{lang["使用"]}{event.item}"
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type,world)

        fire_pattern = r"ItemStack\(minecraft:fire_charge\s+x\s*\d+\)"
        if re.match(fire_pattern, item_str):# 火焰弹
            name = event.player.name
            blocktype = event.block.type
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = f"{blocktype}，{lang["使用"]}{event.item}"
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type,world)
            
        if event.block.type == "minecraft:bed":# 床
            name = event.player.name
            blocktype = event.block.type
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = f"{blocktype}，{lang["使用"]}{event.item}"
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type,world)
            
        if event.block.type == "minecraft:respawn_anchor":# 重生锚
            name = event.player.name
            blocktype = event.block.type
            action = lang["交互"]
            x = event.block.x
            y = event.block.y
            z = event.block.z
            type = f"{blocktype}，{lang["使用"]}{event.item}"
            world = event.block.location.dimension.name
            record_data(name, action, x, y, z, type,world)
       
# 方块破坏事件
    @event_handler
    def blockbreak(self, event: BlockBreakEvent):
        def record_data(name, action, x, y, z,type,world,blockdata):
            # """记录玩家的交互行为到data.json文件中"""
            interaction = {
                'name': name,
                'action': action,
                'coordinates': {'x': x, 'y': y, 'z': z},
                'time': datetime.now().isoformat(),  # 记录当前时间
                'type': type,
                'world': world,
                'blockdata': blockdata
            }  
            with lock:  # 确保线程安全
                breakrec_data.append(interaction)                  
            #threading.Thread(target=write_to_file).start()
            
            # 仅自然方块记录
        if blockrec == 1:
            if event.block.type in [
                "minecraft:stone","minecraft:granite","minecraft:diorite","minecraft:andesite","minecraft:grass_block","minecraft:dirt","minecraft:coarse_dirt","minecraft:podzol",
                "minecraft:sand","minecraft:red_sand","minecraft:gravel","minecraft:gold_ore","minecraft:iron_ore","minecraft:coal_ore","minecraft:oak_log","minecraft:spruce_log",
                "minecraft:birch_log","minecraft:jungle_log","minecraft:oak_leaves","minecraft:spruce_leaves","minecraft:birch_leaves","minecraft:jungle_leaves","minecraft:sponge","minecraft:wet_sponge",
                "minecraft:lapis_ore","minecraft:cobweb","minecraft:short_grass","minecraft:fern","minecraft:dead_bush","minecraft:dandelion","minecraft:poppy","minecraft:blue_orchid",
                "minecraft:allium","minecraft:azure_bluet","minecraft:red_tulip","minecraft:orange_tulip","minecraft:white_tulip","minecraft:oxeye_daisy","minecraft:brown_mushroom","minecraft:obsidian",
                "minecraft:diamond_ore","minecraft:redstone_ore","minecraft:snow","minecraft:ice","minecraft:snow_block","minecraft:cactus","minecraft:clay","minecraft:pumpkin","minecraft:netherrack",
                "minecraft:glowstone","minecraft:brown_mushroom_block","minecraft:red_mushroom_block","minecraft:mushroom_stem","minecraft:melon","minecraft:vine","minecraft:mycelium","minecraft:lily_pad",
                "minecraft:nether_wart","minecraft:end_stone","minecraft:emerald_ore","minecraft:nether_quartz_ore","minecraft:acacia_leaves","minecraft:dark_oak_leaves",
                "minecraft:acacia_log","minecraft:dark_oak_log","minecraft:prismarine","minecraft:hay_block",
                "minecraft:packed_ice","minecraft:sunflower","minecraft:lilac","minecraft:tall_grass","minecraft:large_fern","minecraft:rose_bush",
                "minecraft:peony","minecraft:red_sandstone","minecraft:chorus_plant","minecraft:chorus_flower","minecraft:dirt_path","minecraft:magma_block",
                "minecraft:nether_wart_block","minecraft:bone_block","minecraft:blue_ice","minecraft:seagrass","minecraft:tall_seagrass","minecraft:kelp",
                "minecraft:bamboo","minecraft:cornflower","minecraft:lily_of_the_valley","minecraft:sweet_berry_bush","minecraft:crimson_nylium","minecraft:crimson_stem",
                "minecraft:crimson_fungus","minecraft:crimson_roots","minecraft:warped_nylium","minecraft:warped_stem","minecraft:warped_fungus","minecraft:warped_roots","minecraft:warped_wart_block",
                "minecraft:ancient_debris","minecraft:crying_obsidian","minecraft:blackstone","minecraft:nether_gold_ore","minecraft:basalt","minecraft:nether_sprouts",
                "minecraft:weeping_vines","minecraft:twisting_vines","minecraft:shroomlight","minecraft:soul_soil","minecraft:azalea","minecraft:flowering_azalea","minecraft:azalea_leaves",
                "minecraft:flowering_azalea_leaves","minecraft:moss_carpet","minecraft:moss_block","minecraft:hanging_roots","minecraft:spore_blossom","minecraft:small_dripleaf",
                "minecraft:big_dripleaf","minecraft:glow_lichen","minecraft:small_amethyst_bud","minecraft:medium_amethyst_bud","minecraft:medium_amethyst_bud","minecraft:large_amethyst_bud",
                "minecraft:amethyst_cluster","minecraft:pointed_dripstone","minecraft:deepslate","minecraft:calcite","minecraft:tuff","minecraft:dripstone_block","minecraft:rooted_dirt",
                "minecraft:deepslate_coal_ore","minecraft:deepslate_iron_ore","minecraft:copper_ore","minecraft:deepslate_copper_ore","minecraft:deepslate_gold_ore","minecraft:deepslate_redstone_ore",
                "minecraft:deepslate_emerald_ore","minecraft:deepslate_lapis_ore","minecraft:deepslate_diamond_ore","minecraft:amethyst_block","minecraft:budding_amethyst","minecraft:mangrove_log",
                "minecraft:mangrove_leaves","minecraft:mangrove_roots","minecraft:muddy_mangrove_roots","minecraft:mud","minecraft:cherry_log","minecraft:cherry_leaves","minecraft:torchflower","minecraft:pink_petals",
                "minecraft:pitcher_plant"
            ]:
                name = event.player.name
                action = lang["破坏"]
                x = event.block.x
                y = event.block.y
                z = event.block.z
                type = event.block.type
                world = event.block.location.dimension.name
                turnblock = event.block.data.block_states
                blockdata = f" [{', '.join([f'"{key}"={value}' if isinstance(value, (bool, int, float)) else f'"{key}"="{value}"' for key, value in turnblock.items()])}]"
                record_data(name, action, x, y, z,type,world,blockdata)

        # 全开
        if blockrec == 2:
            if True:
                name = event.player.name
                action = lang["破坏"]
                x = event.block.x
                y = event.block.y
                z = event.block.z
                type = event.block.type
                world = event.block.location.dimension.name
                turnblock = event.block.data.block_states
                blockdata = f" [{', '.join([f'"{key}"={value}' if isinstance(value, (bool, int, float)) else f'"{key}"="{value}"' for key, value in turnblock.items()])}]"
                record_data(name, action, x, y, z,type,world,blockdata)
                
        # 仅人造方块记录
        if blockrec == 4:
            if event.block.type in [
                "minecraft:stone","minecraft:granite","minecraft:diorite","minecraft:andesite","minecraft:grass_block","minecraft:dirt","minecraft:coarse_dirt","minecraft:podzol",
                "minecraft:sand","minecraft:red_sand","minecraft:gravel","minecraft:gold_ore","minecraft:iron_ore","minecraft:coal_ore","minecraft:oak_log","minecraft:spruce_log",
                "minecraft:birch_log","minecraft:jungle_log","minecraft:oak_leaves","minecraft:spruce_leaves","minecraft:birch_leaves","minecraft:jungle_leaves","minecraft:sponge","minecraft:wet_sponge",
                "minecraft:lapis_ore","minecraft:cobweb","minecraft:short_grass","minecraft:fern","minecraft:dead_bush","minecraft:dandelion","minecraft:poppy","minecraft:blue_orchid",
                "minecraft:allium","minecraft:azure_bluet","minecraft:red_tulip","minecraft:orange_tulip","minecraft:white_tulip","minecraft:oxeye_daisy","minecraft:brown_mushroom","minecraft:obsidian",
                "minecraft:diamond_ore","minecraft:redstone_ore","minecraft:snow","minecraft:ice","minecraft:snow_block","minecraft:cactus","minecraft:clay","minecraft:pumpkin","minecraft:netherrack",
                "minecraft:glowstone","minecraft:brown_mushroom_block","minecraft:red_mushroom_block","minecraft:mushroom_stem","minecraft:melon","minecraft:vine","minecraft:mycelium","minecraft:lily_pad",
                "minecraft:nether_wart","minecraft:end_stone","minecraft:emerald_ore","minecraft:nether_quartz_ore","minecraft:acacia_leaves","minecraft:dark_oak_leaves",
                "minecraft:acacia_log","minecraft:dark_oak_log","minecraft:prismarine","minecraft:hay_block",
                "minecraft:packed_ice","minecraft:sunflower","minecraft:lilac","minecraft:tall_grass","minecraft:large_fern","minecraft:rose_bush",
                "minecraft:peony","minecraft:red_sandstone","minecraft:chorus_plant","minecraft:chorus_flower","minecraft:dirt_path","minecraft:magma_block",
                "minecraft:nether_wart_block","minecraft:bone_block","minecraft:blue_ice","minecraft:seagrass","minecraft:tall_seagrass","minecraft:kelp",
                "minecraft:bamboo","minecraft:cornflower","minecraft:lily_of_the_valley","minecraft:sweet_berry_bush","minecraft:crimson_nylium","minecraft:crimson_stem",
                "minecraft:crimson_fungus","minecraft:crimson_roots","minecraft:warped_nylium","minecraft:warped_stem","minecraft:warped_fungus","minecraft:warped_roots","minecraft:warped_wart_block",
                "minecraft:ancient_debris","minecraft:crying_obsidian","minecraft:blackstone","minecraft:nether_gold_ore","minecraft:basalt","minecraft:nether_sprouts",
                "minecraft:weeping_vines","minecraft:twisting_vines","minecraft:shroomlight","minecraft:soul_soil","minecraft:azalea","minecraft:flowering_azalea","minecraft:azalea_leaves",
                "minecraft:flowering_azalea_leaves","minecraft:moss_carpet","minecraft:moss_block","minecraft:hanging_roots","minecraft:spore_blossom","minecraft:small_dripleaf",
                "minecraft:big_dripleaf","minecraft:glow_lichen","minecraft:small_amethyst_bud","minecraft:medium_amethyst_bud","minecraft:medium_amethyst_bud","minecraft:large_amethyst_bud",
                "minecraft:amethyst_cluster","minecraft:pointed_dripstone","minecraft:deepslate","minecraft:calcite","minecraft:tuff","minecraft:dripstone_block","minecraft:rooted_dirt",
                "minecraft:deepslate_coal_ore","minecraft:deepslate_iron_ore","minecraft:copper_ore","minecraft:deepslate_copper_ore","minecraft:deepslate_gold_ore","minecraft:deepslate_redstone_ore",
                "minecraft:deepslate_emerald_ore","minecraft:deepslate_lapis_ore","minecraft:deepslate_diamond_ore","minecraft:amethyst_block","minecraft:budding_amethyst","minecraft:mangrove_log",
                "minecraft:mangrove_leaves","minecraft:mangrove_roots","minecraft:muddy_mangrove_roots","minecraft:mud","minecraft:cherry_log","minecraft:cherry_leaves","minecraft:torchflower","minecraft:pink_petals",
                "minecraft:pitcher_plant"
            ]:
                return False
            else :
                name = event.player.name
                action = lang["破坏"]
                x = event.block.x
                y = event.block.y
                z = event.block.z
                type = event.block.type
                world = event.block.location.dimension.name
                turnblock = event.block.data.block_states
                blockdata = f" [{', '.join([f'"{key}"={value}' if isinstance(value, (bool, int, float)) else f'"{key}"="{value}"' for key, value in turnblock.items()])}]"
                record_data(name, action, x, y, z,type,world,blockdata)
                
# 生物被打事件
    @event_handler
    def animal(self, event: ActorKnockbackEvent):
        def record_data(name, action, x, y, z,type,world):
            # """记录玩家的交互行为到data.json文件中"""
            interaction = {
                'name': name,
                'action': action,
                'coordinates': {'x': x, 'y': y, 'z': z},
                'time': datetime.now().isoformat(),  # 记录当前时间
                'type': type,
                'world': world
            }  
            with lock:  # 确保线程安全
                animalrec_data.append(interaction)                  
            #threading.Thread(target=write_to_file).start()
            
            # 仅重要生物记录
        if nbanimal == 1:
            if event.actor.name in [
                "Horse","Pig","Wolf","Cat","Sniffer","Parrot","Donkey","Mule","Villager","Allay"
            ]:
                name = event.source.name
                action = lang["攻击"]
                x = event.actor.location.x
                y = event.actor.location.y
                z = event.actor.location.z
                type = event.actor.name
                world = event.actor.location.dimension.name
                record_data(name,action, x, y, z,type,world)

        # 全开
        else:
            if True:
                name = event.source.name
                action = lang["攻击"]
                x = event.actor.location.x
                y = event.actor.location.y
                z = event.actor.location.z
                type = event.actor.name
                world = event.actor.location.dimension.name
                record_data(name,action, x, y, z,type,world)   
 

# 方块放置事件
    @event_handler
    def blockplace(self, event: BlockPlaceEvent):
        def record_data(name, action, x, y, z,type,world):
            # """记录玩家的交互行为到data.json文件中"""
            interaction = {
                'name': name,
                'action': action,
                'coordinates': {'x': x, 'y': y, 'z': z},
                'time': datetime.now().isoformat(),  # 记录当前时间
                'type': type,
                'world': world
            }  
            with lock:  # 确保线程安全
                placerec_data.append(interaction)                  
        #threading.Thread(target=write_to_file).start()
        name = event.player.name
        action = lang["放置"]
        x = event.block_placed_state.x
        y = event.block_placed_state.y
        z = event.block_placed_state.z
        type = event.block_placed_state.type
        world = event.block_placed_state.location.dimension.name
        record_data(name,action, x, y, z,type,world)
        
        
    # 与生物交互事件
    @event_handler
    def actorjh(self, event: PlayerInteractActorEvent):
        def record_data(name, action, x, y, z,type,world):
            # """记录玩家的交互行为到data.json文件中"""
            interaction = {
                'name': name,
                'action': action,
                'coordinates': {'x': x, 'y': y, 'z': z},
                'time': datetime.now().isoformat(),  # 记录当前时间
                'type': type,
                'world': world
            }  
            with lock:  # 确保线程安全
                actorrec_data.append(interaction)                  
        #threading.Thread(target=write_to_file).start()
        name = event.player.name
        action = lang["交互"]
        x = event.actor.location.block_x
        y = event.actor.location.block_y
        z = event.actor.location.block_z
        type = event.actor.name
        world = event.actor.location.dimension.name
        record_data(name,action, x, y, z,type,world)
        

# 用于调试的事件
#    @event_handler
#    def blocktest(self,event: PlayerInteractEvent ):  
#        player = event.player
#        inv = player.inventory
#        self.server.broadcast_message(ColorFormat.YELLOW + f"{event.player.name}" + "位置" f"{event.block.x}"" " + f"{event.block.y}"" " + f"{event.block.z}" + f"{event.block.type}" + f"{event.block.location.dimension.name}" + f"{event.item}" + f"{inv}")
# 用于调试的事件
#    @event_handler
#    def test(self,event: BlockBreakEvent): 
#        current_tps = self.server.current_tps
#        self.server.broadcast_message(f"{current_tps}") 
#        turnblock = event.block.data.block_states
#        blockdata = f" [{', '.join([f'{key}={value}' if isinstance(value, (bool, int, float)) else f'"{key}"="{value}"' for key, value in turnblock.items()])}]"
#        turnblock = event.block.data.block_states
#        blockdata = ', '.join([f'"{key}"={value}' if isinstance(value, (bool, int, float)) else f'"{key}"="{value}"' for key, value in turnblock.items()])
#        blockdata = f" [{', '.join([f'"{key}"={value}' if isinstance(value, (bool, int, float)) else f'"{key}"="{value}"' for key, value in turnblock.items()])}]"
#        self.server.broadcast_message(ColorFormat.YELLOW + f"{event.block.type} blockdata: {blockdata}")
# 用于调试的命令发送事件
#    @event_handler
#    def test(self,event: PlayerCommandEvent):  
#        self.server.broadcast_message(ColorFormat.YELLOW + f"{event.player.name}" + f"{PlayerCommandEvent.command}" + " " + f"{Player.address}")
        
# 记录玩家命令的字典


    # 检查命令刷屏，10秒内12条视为刷屏
    @event_handler    
    def commandsban(self, event: PlayerCommandEvent):
        def ban(playername,reason):
            # 检查文件是否存在
            if not os.path.exists(banlist):
                # 如果文件不存在，创建一个空的黑名单文件
                with open(banlist, 'w') as file:
                    json.dump({}, file)

            # 读取黑名单文件
            with open(banlist, 'r') as file:
                blacklist = json.load(file)
            # 将玩家名和理由写入黑名单
            blacklist[playername] = reason
            # 将更新后的黑名单写回文件
            with open(banlist, 'w', encoding='utf-8') as file:  # 指定编码为 UTF-8
                json.dump(blacklist, file, ensure_ascii=False, indent=4)
            self.logger.info(f"{lang["玩家"]} {playername} {lang["已被加入黑名单，理由"]}:{reason}")
        player_name = event.player.name
        #command = PlayerCommandEvent.command
        current_time = tm.time()
        
        # 记录玩家的命令和时间
        player_commands[player_name].append(current_time)
        
        # 保留最近10秒内的命令
        player_commands[player_name] = [t for t in player_commands[player_name] if current_time - t <= 10]
        
        # 检查10秒内命令数量是否超过阈值
        if len(player_commands[player_name]) > 12:  # 阈值为12
            reason = lang["你因涉嫌短时间内发送多条命令被ban"]
            event.player.kick(reason)
            #self.logger.info(f"{player_name}" + f"{reason}")
            playername = player_name
            ban(playername,reason)
            self.server.broadcast_message(f"{playername}{lang["因涉嫌短时间内发送多条命令被ban"]}")
            player_commands[player_name] = []  # 清空记录
            
    # 检查聊天刷屏，10秒内发送6条消息视为刷屏
    @event_handler    
    def chatban(self, event: PlayerChatEvent):
        def ban(playername,reason):
            # 检查文件是否存在
            if not os.path.exists(banlist):
                # 如果文件不存在，创建一个空的黑名单文件
                with open(banlist, 'w',encoding='utf-8') as file:
                    json.dump({}, file)

            # 读取黑名单文件
            with open(banlist, 'r', encoding='utf-8') as file:
                blacklist = json.load(file)
            # 将玩家名和理由写入黑名单
            timestamp = datetime.now().isoformat()  # 使用当前时间戳作为默认值
            # 创建包含所有信息的新条目
            entry = {
                "reason": reason,
                "timestamp": timestamp
            }
            blacklist[playername] = entry

            # 将更新后的黑名单写回文件
            with open(banlist, 'w', encoding='utf-8') as file:  # 指定编码为 UTF-8
                json.dump(blacklist, file, ensure_ascii=False, indent=4)
            self.logger.info(f"{lang["玩家"]} {playername} {lang["已被加入黑名单，理由"]}:{reason}")
        player_name = event.player.name
        #command = PlayerCommandEvent.command
        current_time = tm.time()
        
        # 记录玩家的命令和时间
        player_message[player_name].append(current_time)
        
        # 保留最近10秒内的命令
        player_message[player_name] = [t for t in player_message[player_name] if current_time - t <= 10]
        
        # 检查60秒内命令数量是否超过阈值
        if len(player_message[player_name]) > 6:  # 阈值为6
            reason = lang["你因涉嫌短时间内发送多条消息被ban"]
            event.player.kick(reason)
            #self.logger.info(f"{player_name}" + f"{reason}")
            playername = player_name
            ban(playername,reason)
            self.server.broadcast_message(f"{playername}{lang["因涉嫌短时间内发送多条消息被ban"]}")
            player_message[player_name] = []  # 清空记录
        
    # 检测ban玩家
    @event_handler
    def banjoin(self, event: PlayerJoinEvent):
        playername = event.player.name
        player = event.player
        device_id = getattr(player,'device_id', '未知设备ID')
        # 检查文件是否存在
        if not os.path.exists(banlist):
            # 如果文件不存在，创建一个空的黑名单文件
            with open(banlist, 'w') as file:
                json.dump({}, file)
        if not os.path.exists(banidlist):
            # 如果文件不存在，创建一个空的黑名单文件
            with open(banidlist, 'w') as file:
                json.dump({}, file)

        # 读取黑名单文件
        with open(banlist, 'r', encoding='utf-8') as file:
            blacklist = json.load(file)
        with open(banidlist, 'r', encoding='utf-8') as file:
            blackidlist = json.load(file)
        
        # 检查玩家是否在黑名单中
        if playername in blacklist:
            entry = blacklist[playername]
            reason = entry.get("reason")
            timestamp = entry.get("timestamp")
            event.player.kick(f"{lang["你已被封禁，理由"]}:{reason},{lang["被封禁时间"]}{timestamp}")
            self.logger.info(f"{lang["玩家"]} {playername} {lang["处于封禁名单中，已被踢出，封禁理由为"]}:{reason}")
        # 检查玩家设备ID是否在黑名单中
        if device_id in blackidlist:
            entry = blackidlist[device_id]
            timestamp = entry.get("timestamp")
            event.player.kick(f"{lang["你的设备已于"]}{timestamp}{lang["被封禁"]}")
            self.logger.info(f"{lang["被封禁的设备ID"]} {device_id} {lang["试图加入服务器，已被踢出"]}")
        else:
            return False
        
    @event_handler
    def joinmsg(self, event: PlayerJoinEvent):
        player = event.player
        pname = player.name
        #pip = player.address.hostname
        pid = getattr(player, 'device_id', '未知设备ID')
        pos = getattr(player, 'device_os', '未知系统')
        self.logger.info(f"{ColorFormat.YELLOW}{lang["玩家"]} {pname}({lang["设备ID"]}:{pid} {lang["系统名称"]}:{pos}) {lang["加入了游戏"]}")
        
            
        
player_commands = defaultdict(list)
player_message = defaultdict(list)