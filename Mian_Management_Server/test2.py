import re
import os

p = r"E:\CodeBase\Go\src\construct_manager_server\models\sass"
template = '<el-table-column prop="%s" label="%s"></el-table-column>'
input_temp = '<el-form-item label="%s" prop="%s"> \n  <el-input v-model="temp.%s" placeholder="请输入"/> \n</el-form-item>'
sq_temp = '%s = Column(%s, nullable=False, server_default="", comment="%s")'
top = 'from server import db\nfrom sqlalchemy import Column, String, DECIMAL, DateTime, Boolean, func, text\nfrom sqlalchemy.dialects.mysql import INTEGER, TINYINT, MEDIUMINT, BIGINT'
end = '    def to_dict(self):\n        result = {}\n        for k, v in self.__table__.columns:\n            result[k] = v\n        return result'

# tar_dir = r"C:\Users\Administrator\Desktop\tem"
tar_dir = r"C:\Users\Administrator\Desktop\temp"


def generate(path, filename):
    with open(path, "r", encoding='utf-8') as f:
        x = f.read()
    # print(x)
    n = re.findall(r"type (.*?) struct[\s\S]*?gorm\.Model([\s\S]*?)(\}[\s\S]*)", x)
    if not n:
        return
    start = n[0][0]
    m_name = start
    content = n[0][1]
    # end = n[0][2]
    start = top + '\n\n\n' + 'class %s(db.Model):' % start
    print(start, content)

    decs = re.findall(r"(.*?) (.*?) (.*?comment:')(.*)('.*?json:\"(.*?)\")", content)
    # new_content = ""
    # new_temp = ""
    new_input_temp = start
    for dec in decs:
        new_input_temp += "\n" + sq_temp % (dec[0], dec[1], dec[3])

    new_input_temp += "\n\n" + end
    print(new_input_temp)
    res_dir = tar_dir + "\\" + m_name + '.py'
    print(res_dir)
    with open(res_dir, 'w', encoding='utf-8') as f:
        f.write(new_input_temp)


for i in os.listdir(p):
    pa = os.path.join(p, i)
    generate(pa, i)
