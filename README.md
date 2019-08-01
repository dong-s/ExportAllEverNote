## 批量导出EverNote中的所有笔记

印象笔记客户端中，导出笔记这个功能不能支持全量一次性导出，只能按笔记或者笔记本来导出，并且导出的笔记需要自己手工维护路径，感觉有点麻烦。

本地备份一方面比较安全，另一方面如果印象笔记以后不提供服务了，可以直接将导出的文件恢复到其他笔记应用，目前大部分笔记应用都支持enex文件导入。

通过使用该工具可以将笔记按**笔记本组/笔记本/笔记.enex**路径来导出。

## Token获取

**1.页面申请:**
- [印象笔记](https://app.yinxiang.com/api/DeveloperToken.action)
- [Evernote](https://www.evernote.com/api/DeveloperToken.action)

**2.网页获取：**
登录印象笔记首页：
![](http://file.dong-s.com/2019/08/evernote.jpg)


## 安装

```bash
pip install evernote-export
```

## Usage

```bash
$ evernote-export
Usage: evernote-export [options]

Options:
  -h, --help            show this help message and exit
  -t TOKEN, --token=TOKEN
                        evernote_api_token
  -d DIR, --dir_path=DIR
                        export dir path
  --sandbox_model       is sandbox model,default False
  --china_user          is chinese user,default False

# token和导出文件路径是必选参数
# 注意：指定的导出路径在运行时会先清空
$ evernote-export -t your_api_token -d /home/dong/evernote --china_user
```

## 导出文件示例

```
$ tree
.
├── EverMemo
│   ├── xxxx.enex
│   ├── xxx.enex
│   └── xxx.enex
├── 大数据
│   ├── hadoop
│   │   ├──xxxx.enex
│   │   ├── xxxx.enex
│   │   └── xxxx.enex
│   ├── hbase
│   │   ├── xxxx.enex
│   │   ├── xxxx.enex
│   │   └── xxxx.enex
│   ├── hive
│   │   ├── xxxx.enex
│   │   └── xxxx.enex
│   └── spark
│       ├── xxxx.enex
│       └── xxxx.enex
└── 个人
    └── 随笔
        ├── xxx.enex
        └── xxx.enex

```

## 注意事项

- 笔记的tag未导出
- 笔记标题中特殊字符[/\\\s<>]，会被替换为下划线
- 仅在Mac和linux系统Python2.7环境下测试过，Python3不支持



