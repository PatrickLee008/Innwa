import os
import re
from typing import List


def remove_insert_statements(sql_file: str, table_names: List[str], output_file: str = None):
    """
    删除 SQL 文件中与指定表名相关的 INSERT 语句。

    :param sql_file: SQL 文件的路径。
    :param table_names: 需要移除 INSERT 语句的表名列表。
    :param output_file: 输出的文件路径，默认为 None，会生成一个 _modified.sql 文件。
    :return: None
    """
    if not os.path.exists(sql_file):
        raise FileNotFoundError(f"SQL 文件 {sql_file} 不存在。")

    # 构造匹配 INSERT 语句的正则表达式
    # 支持表名前带反引号 (`) 或无引号的情况
    table_regex = "|".join(
        fr"(?:`)?{re.escape(table)}(?:`)?"
        for table in table_names
    )
    insert_regex = re.compile(
        rf"INSERT\s+INTO\s+({table_regex})\s+.*?;",
        re.IGNORECASE | re.DOTALL
    )

    # 读取文件内容
    with open(sql_file, 'r', encoding='utf-8') as file:
        sql_content = file.read()

    # 删除匹配的 INSERT 语句
    modified_sql = insert_regex.sub("", sql_content)

    modified_sql = "\n".join(
        line for line in modified_sql.splitlines() if line.strip()
    )

    # 如果没有指定输出文件，则生成一个默认名称
    if output_file is None:
        base, ext = os.path.splitext(sql_file)
        output_file = f"{base}_modified{ext}"

    # 保存修改后的内容
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(modified_sql)

    print(f"修改后的 SQL 已保存到: {output_file}")


# 示例使用
if __name__ == "__main__":
    # 假设当前目录有一个文件 script.sql
    sql_file_path = "db_innwa_20241124_160001.sql"
    tables_to_remove = ["order_history", "m_app_operation", "m_tran_settlement", "m_login_record", "m_withdrawal",
                        "m_app_order", "m_play_recharge", "m_app_match", "m_app_match_attr", "m_match_settle",
                        "m_app_order_copy","m_login_record","m_charge_callback","m_app_operation_bak","m_operation","m_app_match_attr_vip","sphinx"]  # 要移除的表
    remove_insert_statements(sql_file_path, tables_to_remove)
