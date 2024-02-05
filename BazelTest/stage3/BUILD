load("@bazel_tools//tools/build_defs/pkg:pkg.bzl", "pkg_tar")

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

#pkg_tar(
#    name = "html_tar",
#    srcs = [":template_files", ":static_files"],
#    package_dir = ".",
#)


#genrule(
#    name = "extract_files",
#    srcs = [":html_tar"],
#    outs = ["static", "templates"],
#    cmd = "echo 'output.log'",
#    visibility = ["//visibility:public"],
#    tools = ["@bazel_tools//tools/tar:tar"],
#)
