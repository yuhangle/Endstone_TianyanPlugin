import sqlite3
from datetime import datetime, timedelta
from endstone_tianyan import zh_lang

# 定义一个全局变量
is_running = False

lang = zh_lang.default_lang

def clean_old_interactions(db_path, hours_threshold):
    """
    清理数据库
    db_path: 数据库路径
    hours_threhold: 时间
    """
    # 声明运行中全局变量
    global is_running,vac_msg,msg1,msg2
    
    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    is_running = True

    # 重构数据库并释放空间
    def vacuum_db(db_path):
        global vac_msg
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # 执行VACUUM命令以整理数据库并尝试减少文件大小
            cursor.execute("VACUUM")
            
            # 提交更改到数据库
            conn.commit()

            vac_msg = lang["清理完成，数据库文件已整理"]
            #print(vac_msg)

        except Exception as e:
            # 如果发生错误，打印错误信息
            vac_msg = f"{lang['发生错误']}:, {e}"
            #print(vac_msg)

        finally:
            # 关闭数据库连接
            conn.close()
        return vac_msg


    try:
        # 获取当前时间，并转换为ISO格式（与SQLite的datetime兼容）
        #now_iso = datetime.now().isoformat()

        # 计算给定小时数之前的时间点，并转换为ISO格式
        cutoff_time = (datetime.now() - timedelta(hours=hours_threshold)).isoformat()

        # 准备SQL语句，用于删除所有早于cutoff_time的数据记录
        delete_query = """
            DELETE FROM interactions
            WHERE time < ?
        """

        # 执行删除查询，并传递cutoff_time作为参数
        cursor.execute(delete_query, (cutoff_time,))
        
        # 提交更改到数据库
        conn.commit()

        # 打印被删除的行数信息
        msg1 = f"{lang['已删除']} {cursor.rowcount} {lang['行']},{lang['这些数据超过']} {hours_threshold} {lang['小时']}"
        #print(msg1)
        vacuum_db(db_path)
        msg2 = f"{lang['已重构数据库释放空间']}"
        #print(msg2)

    except Exception as e:
        # 如果发生错误，打印错误信息并回滚事务
        msg1 = f"{lang['发生错误']}:, {e}"
        #print(msg1)
        conn.rollback()

    finally:
        # 关闭数据库连接
        conn.close()
        is_running = False
        

# 示例用法：
# clean_old_interactions('你的数据库路径.db', 24)  # 删除超过24小时的数据记录