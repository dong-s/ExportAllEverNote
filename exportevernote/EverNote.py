# coding=utf-8
import os
import re
import sys
import time
import base64
import logging
from datetime import datetime
from optparse import OptionParser
from evernote.edam.notestore import NoteStore
from evernote.api.client import EvernoteClient

logging.basicConfig(level=logging.INFO, format="<%(asctime)s> [%(levelname)s] %(message)s")

note_header = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-export SYSTEM "http://xml.evernote.com/pub/evernote-export3.dtd">
<en-export export-date="{}" application="Evernote" version="Evernote Mac 7.2.1 (456793)">
<note><title>{}</title><content><![CDATA[<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">"""

note_mid = """</content><created>{}</created><updated>{}</updated><note-attributes><source>{}</source><source-url>{}</source-url><source-application>{}</source-application><reminder-order>0</reminder-order></note-attributes>"""

note_resource_one = """<resource><data encoding="base64">{}</data><mime>{}</mime><width>{}</width><height>{}</height><duration>0</duration><recognition><![CDATA[{}]]></recognition><resource-attributes><source-url>{}</source-url><timestamp>19700101T000000Z</timestamp><reco-type>unknown</reco-type><file-name>{}</file-name></resource-attributes></resource>"""

note_resource_two = """<resource><data encoding="base64">{}</data><mime>{}</mime><width>{}</width><height>{}</height><duration>0</duration><resource-attributes><source-url>{}</source-url><timestamp>19700101T000000Z</timestamp><file-name>{}</file-name></resource-attributes></resource>"""

note_tail = """</note></en-export>"""

now = datetime.now().strftime('%Y%m%dT%H%M%SZ')


def clear_dir(current_dir):
    """
    清空当前目录
    :param current_dir:
    :return:
    """
    for root, dirs, files in os.walk(current_dir, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))


def create_dir(path):
    """
    创建目录
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.mkdir(path)


def write_file(path, content):
    """
    将生成的文档写入文件
    :param path:
    :param content:
    :return:
    """
    with open(path + ".enex", 'w') as f:
        f.write(content)


def format_str(text, length):
    """
    按指定长度切分文本
    :param text:
    :param length:
    :return:
    """
    arr = []
    for i in range(len(text) / length + 1):
        arr.append(text[i * length:i * length + length])
    return "\n".join(arr)


def format_time(timestamp):
    return time.strftime('%Y%m%dT%H%M%SZ', time.localtime(timestamp / 1000))


class EverNoteCustomClient:
    def __init__(self, token, sandbox, china):
        logging.info("初始化EverNote客户端！")
        self.client = EvernoteClient(token=token, sandbox=sandbox, china=china)
        self.note_store = self.client.get_note_store()

    def list_notebooks(self):
        logging.info("获取所有笔记本！")
        return self.note_store.listNotebooks()

    def get_notes_by_notebookid(self, notebook_guid):
        """
        获取当前笔记本下的所有笔记
        :param notebook_guid:
        :return:
        """
        note_filter = NoteStore.NoteFilter()
        note_filter.notebookGuid = notebook_guid
        return self.note_store.findNotes(note_filter, 0, 999).notes

    def get_note(self, note_guid):
        """
        获取该笔记的完整内容
        :param note_guid:
        :return:
        """
        return self.note_store.getNote(note_guid, True, True, True, True)

    def format_enex_file(self, note_guid):
        """
        组装enex文件
        :param note_guid:
        :return:
        """
        try:
            note = self.note_store.getNote(note_guid, True, True, True, True)

            result = note_header.format(now, note.title)
            result += note.content[note.content.find("<en-note"):]
            result += "]]>"
            if note.attributes.sourceURL:
                note_source_url = note.attributes.sourceURL.replace("&", "&amp;")
            else:
                note_source_url = ""

            result += note_mid.format(format_time(note.created), format_time(note.updated), note.attributes.source,
                                      note_source_url, note.attributes.sourceApplication)
            if note.resources:
                res_list = note.resources
                for res in res_list:
                    if res.attributes.sourceURL:
                        resources_source_url = res.attributes.sourceURL.replace("&", "&amp;")
                    else:
                        resources_source_url = ""

                    if res.recognition:
                        result += note_resource_one.format(format_str(base64.b64encode(res.data.body), 80), res.mime,
                                                           res.width, res.height, res.recognition.body,
                                                           resources_source_url,
                                                           res.attributes.fileName)
                    else:
                        result += note_resource_two.format(format_str(base64.b64encode(res.data.body), 80), res.mime,
                                                           res.width, res.height,
                                                           resources_source_url,
                                                           res.attributes.fileName)
            result += note_tail
            return result
        except Exception as e:
            logging.error("《{}》导出异常！".format(note.title), e)


def main():
    parser = OptionParser()

    parser.add_option("-t", "--token", dest="token", help="evernote_api_token")
    parser.add_option("-d", "--dir_path", dest="dir", help="export dir path")
    parser.add_option('--sandbox_model', dest="sandbox", help='is sandbox model', action='store_true', default=False)
    parser.add_option('--china_user', dest="china", help='is chinese user', action='store_true', default=False)
    (options, args) = parser.parse_args()

    token = options.token
    target_dir = options.dir
    sandbox = options.sandbox
    china = options.china

    note_count = 0
    notebook_count = 0

    if token is None or target_dir is None:
        parser.print_help()
        exit(0)

    logging.info("清空目标文件夹：{}".format(target_dir))
    clear_dir(target_dir)

    client = EverNoteCustomClient(token=token, sandbox=sandbox, china=china)

    notebooks = client.list_notebooks()

    for notebook in notebooks:
        notebook_count += 1
        # 判断当前笔记本是否有上级目录
        logging.info("================================")
        logging.info("开始导出notebook《{}》中的笔记".format(notebook.name))
        if notebook.stack:
            create_dir(os.path.join(target_dir, notebook.stack))
            note_path = os.path.join(target_dir, notebook.stack, notebook.name)
            create_dir(note_path)
        else:
            note_path = os.path.join(target_dir, notebook.name)
            create_dir(note_path)
        logging.info("创建notebook对应的目录：{}".format(note_path))

        notes = client.get_notes_by_notebookid(notebook.guid)

        for note in notes:
            note_count += 1
            logging.info("开始导出笔记《{}》".format(note.title))
            result = client.format_enex_file(note.guid)
            if result:
                write_file(os.path.join(note_path, re.sub(r'[/\\\s<>]', '_', note.title)), result)

        logging.info("当前notebook《{}》已导出完成！".format(notebook.name))

    logging.info("全部笔记已导出，共导出笔记本：{}，共导出笔记：{}".format(notebook_count, note_count))


if __name__ == '__main__':
    main()
