import os

# 业务测试使用连接本机 MySQL 的测试配置；模板自带的纯配置类测试可单独覆盖。
os.environ.setdefault("CONFIG_FILE", "config-test.yaml")
