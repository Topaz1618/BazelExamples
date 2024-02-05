# BazelExamples

[BazelExamples English Version](../README.md)


BazelExamples 提供了使用 Bazel 构建 Python 项目的清晰示例，展示了不同情景的 BUILD 和 WORKSPACE 定义。


## 技术栈
BazelExamples 项目使用了以下技术栈和工具：

- Python
- JavaScript
- Tornado
- HTML/CSS
- gpt-3.5模型：用于文本生成的核心模型。
- Redis：为GPTBot应用提供缓存和数据存储功能
- MongoDB
- MySQL


## 项目实例
### Stage1
- BUILD:
    - Python 构建: 使用 py_binary 规则展示基本应用。
-  WORKSPACE:
    - 远程仓库下载: 通过 rules_python 实现远程仓库下载。
    - Python 相关规则和仓库加载。
### Stage3
- BUILD:
    - Python 构建: 利用 py_binary 规则展示基本应用。
    - 模板文件和静态文件配置: 使用 filegroup() 规则配置模板和静态文件。
- WORKSPACE:
    - 远程仓库下载: 通过 rules_python 实现远程仓库下载。
    - Python 相关规则和仓库加载。
### Stage4
- BUILD:
    - Python 构建: 利用 py_binary 规则展示基本应用。
    - 模板文件和静态文件配置: 使用 filegroup() 规则配置模板和静态文件。
    - 打包和归档: 使用 pkg_tar() 规则将项目打包成 tar 文件。

- WORKSPACE:
    - 远程仓库下载支持: 通过 rules_python 实现远程仓库下载支持。
    - 远程仓库下载支持: 引入 pkg_tar 远程仓库，实现对 pkg_tar() 规则的支持。
    - Python 相关规则和仓库加载。


## 使用

### 构建
```
bazel build //:apps
```

### 运行

根据目标的依赖关系和构建规则执行构建步骤，并运行最终生成的二进制文件
```
bazel run apps
```

or 直接运行生成的二进制文件
```
./bazel-bin/apps
```


### 清理构建目录及缓存
```
bazel clean --expunge
```

### 构建指定目标
这个命令构建的是 :test_tar 这个目标，而不是项目的所有部分
```
bazel build -s --symlink_prefix= :test_tar
```
参数

```
-s 选项用于输出详细构建信息

--symlink_prefix= 选项指定前缀，为空默认构建结果存放在 bazel-bin/ 目录下
```


# 版权和许可
BazelExamples基于[MIT许可证](LICENSE)进行许可。详细信息请参阅许可文件。
如有任何问题或建议，请随时提出。感谢您的使用和贡献！