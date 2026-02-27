#!/usr/bin/env python3
"""
Nacos 配置更新工具 - Python 版本
将本地配置文件发布到 Nacos 配置中心
"""

import argparse
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError

try:
    import nacos
except ImportError:
    print("Error: nacos-sdk-python is not installed")
    print("Please install it with: pip install nacos-sdk-python")
    sys.exit(1)


DEFAULT_SCHEME = "https"
DEFAULT_NACOS_GROUP = "DEFAULT_GROUP"
DEFAULT_HTTP_PORT = 80
DEFAULT_HTTPS_PORT = 443


class NacosUpdater:
    """Nacos 配置更新器"""

    def __init__(self, args):
        self.nacos_addr = args.nacos_addr
        self.nacos_addr_scheme = args.nacos_addr_scheme
        self.nacos_port = args.nacos_port
        self.nacos_ns_id = args.nacos_ns_id
        self.nacos_username = args.nacos_username
        self.nacos_passwd = args.nacos_passwd
        self.nacos_ns_group = args.nacos_ns_group
        self.nacos_filename_list = args.nacos_filename_list

    def validate_params(self):
        """验证必需参数"""
        required_params = {
            "nacos_addr": self.nacos_addr,
            "nacos_addr_scheme": self.nacos_addr_scheme,
            "nacos_ns_id": self.nacos_ns_id,
            "nacos_username": self.nacos_username,
            "nacos_passwd": self.nacos_passwd,
            "nacos_ns_group": self.nacos_ns_group,
            "nacos_filename_list": self.nacos_filename_list,
        }

        missing_params = [key for key, value in required_params.items() if not value]

        if missing_params:
            print(f"入参异常: 缺少必需参数 {', '.join(missing_params)}")
            return False

        return True

    def run(self):
        """执行配置发布"""
        if not self.validate_params():
            return

        # 构建 Nacos 服务器地址
        # nacos-sdk-python 需要的格式: scheme://host:port
        server_address = f"{self.nacos_addr_scheme}://{self.nacos_addr}:{self.nacos_port}"

        try:
            # 创建 Nacos 客户端
            # endpoint 参数用于指定 context path
            client = nacos.NacosClient(
                server_addresses=server_address,
                namespace=self.nacos_ns_id,
                username=self.nacos_username,
                password=self.nacos_passwd,
                endpoint="/nacos",
                log_level="INFO",
            )

            # 解析文件名列表
            file_list = [f.strip() for f in self.nacos_filename_list.split(",")]

            # 处理每个文件
            for file_path in file_list:
                try:
                    # 读取文件内容
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 获取文件名（不含路径）
                    data_id = Path(file_path).name

                    # 发布配置到 Nacos
                    success = client.publish_config(
                        data_id=data_id,
                        group=self.nacos_ns_group,
                        content=content,
                        config_type="yaml",
                    )

                    if success:
                        print(f"✅ Nacos config {file_path} published successfully")
                    else:
                        print(f"❌ Failed to publish nacos config {file_path}")

                except FileNotFoundError:
                    print(f"❌ Error: File not found - {file_path}")
                    continue
                except HTTPError as e:
                    if e.code == 403:
                        print(f"❌ Error: Permission denied when publishing {file_path}")
                        print(f"  Please check if you have write permission for group '{self.nacos_ns_group}' in namespace '{self.nacos_ns_id}'")
                    elif e.code == 404:
                        print(f"❌ Error: Config endpoint not found when publishing {file_path}")
                        print(f"  Please check the Nacos server address and context path")
                    else:
                        print(f"❌ Error publishing nacos config {file_path}: HTTP {e.code}")
                    continue
                except Exception as e:
                    print(f"❌ Error publishing nacos config {file_path}: {e}")
                    continue

        except HTTPError as e:
            if e.code == 403:
                print("=" * 60)
                print("❌ Authentication Failed!")
                print("=" * 60)
                print(f"Error: Username or password is incorrect")
                print(f"")
                print(f"Please check your credentials:")
                print(f"  - Username: {self.nacos_username}")
                print(f"  - Password: {'*' * len(self.nacos_passwd)}")
                print(f"  - Namespace: {self.nacos_ns_id}")
                print(f"")
                print(f"If credentials are correct, please verify:")
                print(f"  1. User account exists in Nacos")
                print(f"  2. User has access to namespace '{self.nacos_ns_id}'")
                print("=" * 60)
            elif e.code == 404:
                print("=" * 60)
                print("❌ Server Connection Failed!")
                print("=" * 60)
                print(f"Error: Nacos server endpoint not found (HTTP 404)")
                print(f"")
                print(f"Server address: {server_address}/nacos")
                print(f"")
                print(f"Please check:")
                print(f"  1. Server address is correct: {self.nacos_addr}")
                print(f"  2. Port is correct: {self.nacos_port}")
                print(f"  3. Nacos context path is '/nacos'")
                print("=" * 60)
            else:
                print("=" * 60)
                print("❌ HTTP Error!")
                print("=" * 60)
                print(f"Error Code: {e.code}")
                print(f"Server: {server_address}/nacos")
                print(f"Details: {e}")
                print("=" * 60)
            sys.exit(1)
        except URLError as e:
            print("=" * 60)
            print("❌ Network Connection Failed!")
            print("=" * 60)
            print(f"Error: Cannot connect to Nacos server")
            print(f"")
            print(f"Server address: {server_address}/nacos")
            print(f"")
            print(f"Please check:")
            print(f"  1. Network connection is available")
            print(f"  2. Server address is correct: {self.nacos_addr}")
            print(f"  3. Firewall allows access to port {self.nacos_port}")
            print(f"  4. Nacos server is running")
            print(f"")
            print(f"Details: {e.reason}")
            print("=" * 60)
            sys.exit(1)
        except Exception as e:
            print("=" * 60)
            print("❌ Unexpected Error!")
            print("=" * 60)
            print(f"Error: {type(e).__name__}")
            print(f"Details: {e}")
            print(f"")
            print(f"Server: {server_address}/nacos")
            print(f"Namespace: {self.nacos_ns_id}")
            print("=" * 60)
            sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="更新 Nacos 配置文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python update_nacos.py \\
    --nacos-addr nacos.xxx.com \\
    --nacos-addr-scheme https \\
    --nacos-port 443 \\
    --nacos-ns-id test \\
    --nacos-username test \\
    --nacos-passwd test \\
    --nacos-ns-group DEFAULT_GROUP \\
    --nacos-filename-list test1.yml,test2.yml
        """,
    )

    parser.add_argument(
        "--nacos-addr",
        "-a",
        required=True,
        help="Nacos 服务器地址",
    )

    parser.add_argument(
        "--nacos-addr-scheme",
        "-s",
        default=DEFAULT_SCHEME,
        choices=["http", "https"],
        help=f"Nacos 地址协议 (默认: {DEFAULT_SCHEME})",
    )

    parser.add_argument(
        "--nacos-port",
        "-t",
        type=int,
        help="Nacos 端口 (默认: http=80, https=443)",
    )

    parser.add_argument(
        "--nacos-ns-id",
        "-n",
        required=True,
        help="Nacos 命名空间 ID",
    )

    parser.add_argument(
        "--nacos-username",
        "-u",
        required=True,
        help="Nacos 用户名",
    )

    parser.add_argument(
        "--nacos-passwd",
        "-p",
        required=True,
        help="Nacos 密码",
    )

    parser.add_argument(
        "--nacos-ns-group",
        "-g",
        default=DEFAULT_NACOS_GROUP,
        help=f"Nacos 命名空间组 (默认: {DEFAULT_NACOS_GROUP})",
    )

    parser.add_argument(
        "--nacos-filename-list",
        "-f",
        required=True,
        help="Nacos 配置文件名列表 (逗号分隔)",
    )

    args = parser.parse_args()

    # 如果没有指定端口，根据协议设置默认端口
    if args.nacos_port is None:
        if args.nacos_addr_scheme == "https":
            args.nacos_port = DEFAULT_HTTPS_PORT
        else:
            args.nacos_port = DEFAULT_HTTP_PORT

    # 创建更新器并执行
    updater = NacosUpdater(args)
    updater.run()


if __name__ == "__main__":
    main()
