load("@rules_pkg//pkg:tar.bzl", "pkg_tar")

#load("@bazel_tools//tools/build_defs/pkg:pkg.bzl", "pkg_tar")

py_binary(
    name = "apps",
    srcs = ["apps.py"],
    data = [":template_files", ":static_files"],
)


filegroup(
    name = "template_files",
    srcs = glob(["templates/index.html"]),
    visibility = ["//visibility:public"],
)

filegroup(
    name = "static_files",
    srcs = glob(["static/**"]),
    visibility = ["//visibility:public"],
)

# package all files and unpack automically
#pkg_tar(
#    name = "test_tar",
#    srcs = glob(["*"]),
    # srcs = [":apps", ":template_files", ":static_files"], # Only files no file structure
    #package_dir = ".",
    #package_dir = "//:test_tar", # the final tar name
#    out = "test_tar.tar",
#)

pkg_tar(
    name = "test_tar",
    #srcs = glob(["*"]),
    srcs = [":apps", ":template_files", ":static_files"], # Only files no file structure
    package_dir = "test_tar", # the final tar name
    out = "test_tar.tar",
)


