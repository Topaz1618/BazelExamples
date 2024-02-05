#load("@bazel_tools//tools/build_defs/pkg:pkg.bzl", "pkg_tar")

load("@rules_pkg//pkg:tar.bzl", "pkg_tar")

py_binary(
    name = "apps",
    srcs = ["apps.py"],
    data = [":template_files", ":static_files"],
    visibility = ["//visibility:public"],
)


filegroup(
    name = "template_files",
    srcs = glob(["templates/**"]),
    visibility = ["//visibility:public"], # 定义了可见范围, 默认private, 值为 public 时, 间接依赖也可用, pkg_tar 就是间接引用。
)


filegroup(
    name = "static_files",
    srcs = glob(["static/**"]),
    visibility = ["//visibility:public"],
)

pkg_tar(
    name = "test_tar",
    srcs = glob(["*"]),
    #srcs = [":apps", ":template_files", ":static_files"], # Only files no file structure
    package_dir = "test_tar", # the final tar name
    out = "test_tar.tar",
)

