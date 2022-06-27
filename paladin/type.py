from enum import Enum


class Ele(Enum):
    BUTTON = '按钮'
    LINKBUTTON = '超链接'
    INPUT = '输入框'
    RICHINPUT = '富文本输入框'
    CHECKBOX = '勾选框'
    RADIOBOX = '单选框'
    SINGLEDROPDOWN = '下拉框'
    MULTIDROPDOWN = '下拉多选框'

    NOTICE = '消息框'
    DATAGRID = '表格'
    CUSTOM = '自定义组件'


class CaseType(Enum):
    UPLOAD = '上传文件'
    WAIT = '等待'
    READIPO = '读取IPO文件'
    LOGIN = '登录'
    MENU = '菜单'
    TREENODE = '树形目录'
    SWITCHMENU = '切换菜单'
    SWITCHTAB = '切换TAB'
    CLOSEMENU = '关闭菜单'
    CLOSEDIAL = '关闭弹窗'
    CASE = '用例'
    SCRIPT = '自定义脚本'


class ExpectType(Enum):
    MESSAGE = '消息提示'
    DBDATASET = '数据库结果'
    DATAGRIDTOTAL = '表格总计'
    DATAGRIDCNT = '表格行数'
    DATAGRID = '表格内容'
    DATAGRIDHAS = '表格包含'
    COLUMNVALUE = '表格某列的值'
    EMAILHAS =  '邮件包含'
    PAGEHAS = '页面包含'
    PAGEHASNOT = '页面不包含'
    TAKESCREEN = '截图'
    ATTACHMENT = '附件'
    SCRIPT = '自定义脚本'


class PreType(Enum):
    UPDATEDB = '更新数据库'
    EXECPROC = '调用存储过程'
    CMD = '批处理'
    DELFILE = '删除附件'
    UPDATECONFIG = '修改配置'
    SCRIPT = '自定义脚本'


if __name__ == '__main__':
    ele = list(x.value for x in Ele)
    ct = list(x.value for x in CaseType)
    print('\r\n'.join(ele + ct))
    print('----------------')
    print('\r\n'.join(list(x.value for x in ExpectType)))
    print('----------------')
    print('\r\n'.join(list(x.value for x in PreType)))
    print('----------------')
