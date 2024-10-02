import re
import subprocess
import sys
import time
from importlib.metadata import distribution, PackageNotFoundError, version
from packaging.version import parse
import inquirer
import requests

update_source = [
    inquirer.List(
        "source",
        message="Please choose the source to update",
        choices=["清华源", "北京外国语", "PyPI"],
    ),
]


def check_for_updates():
    print("Checking for updates...")
    # 获取本地sjtuautorun版本号
    local_version = get_local_version()

    # 发送 GET 请求获取库的元数据信息
    try:
        response = requests.get("https://pypi.tuna.tsinghua.edu.cn/pypi/sjtuautorun/json")
        data = response.json()
        latest_version = data["info"]["version"]
    except requests.ConnectionError:
        print("No network connection, skipping update check.")
        latest_version = None

    if local_version is None:
        print("Failed to get the local version, skipping update check.")
        return

    if latest_version is None:
        print("Failed to get the latest version, skipping update check.")
        return

    # 比较版本号
    if parse(local_version) < parse(latest_version):
        update_questions = [
            inquirer.List(
                "source",
                message=f"New version {latest_version} is available.Your version is {local_version}. Do you want to "
                        f"update?",
                choices=["Yes", "No"],
            ),
        ]
        result = get_user_choice(update_questions)
        if result == "Yes":
            # 选择使用哪个源更新,输出按钮回车选择
            choice = get_user_choice(update_source)
            update_library(choice)
            recent_updates = get_recent_updates_from_pypi(latest_version)
            print("更新内容:\n" + recent_updates)

            print("更新完成，稍后将自动退出，请重新启动脚本")
            time.sleep(5)
            sys.exit(0)  # 更新成功后退出脚本_exit(0)  # 更新成功后退出脚本
    else:
        print("You are using the latest version of the library.")


def get_local_version():
    try:
        distribution('sjtuautorun')
    except PackageNotFoundError as e:
        print(f"Package {e} not found, skipping update check.")
        return

    # Query PyPI index to get the latest version
    response = requests.get(f'https://pypi.org/pypi/sjtuautorun/json')
    if response.status_code == 200:
        data = response.json()
        installed_version = version("sjtuautorun")
        return installed_version
    else:
        return f"Failed to get the latest version, status code: {response.status_code}"


def get_user_choice(questions):
    answers = inquirer.prompt(questions)
    return answers["source"]


def update_library(choice="PyPI"):
    choice_list = {
        "PyPI": [
            "pip",
            "install",
            "--upgrade",
            "--index-url",
            "https://pypi.org/simple",
            "sjtuautorun",
        ],
        "北京外国语": [
            "pip",
            "install",
            "--index-url",
            "https://mirrors.bfsu.edu.cn/pypi/web/simple/",
            "--upgrade",
            "sjtuautorun",
        ],
        "清华源": [
            "pip",
            "install",
            "--index-url",
            "https://pypi.tuna.tsinghua.edu.cn/simple",
            "--upgrade",
            "sjtuautorun",
        ],
    }
    subprocess.run(choice_list[choice])


def get_recent_updates_from_pypi(latest_version):

    url = f"https://pypi.org/project/sjtuautorun/{latest_version}/#description"
    response = requests.get(url)

    if response.status_code == 200:
        readme_content = response.text
        updates_section = re.search(
            r"<h2>近期更新</h2>(.*?)</ul>", readme_content, re.S
        )

        if updates_section:
            updates = updates_section.group(1).strip()
            # 提取所有 <li> 标签中的内容
            updates_list = re.findall(r"<li>(.*?)</li>", updates, re.S)
            # 合并为一个字符串，每行前面加上一个 ·
            updates_text = "\n".join(
                [f'· {re.sub(r"<.*?>", "", update).strip()}' for update in updates_list]
            )
            return updates_text
        else:
            return "未找到近期更新部分。"
    else:
        return f"无法获取更新内容，状态码: {response.status_code}"


# if __name__ == "__main__":
#     check_for_updates()
