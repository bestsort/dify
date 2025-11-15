# coding=utf-8
# pip install docker
import os
import difflib
import docker

REPLACEMENTS = {
    "http://api:5001": "http://docker-api-1:5004",
    "http://web:3000": "http://docker-web-1:3000",
}

client = docker.from_env()
current_dir = os.path.dirname(os.path.abspath(__file__))


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def write_file(file_path: str, content: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"文件写入成功：{file_path} (大小: {os.path.getsize(file_path)} 字节)")


def restart_container(container_name: str) -> None:
    container = client.containers.get(container_name)
    container.restart()


def apply_replacements(content: str) -> str:
    updated = content
    for old, new in REPLACEMENTS.items():
        if old not in updated:
            print(f"警告：未在模板中找到 {old}")
        updated = updated.replace(old, new)
    return updated


def main() -> None:
    template_path = os.path.join(current_dir, "nginx/conf.d/default.conf.template")
    print(f"模板路径：{template_path}")

    try:
        original_content = read_file(template_path)
    except Exception as exc:
        print(f"读取模板失败：{exc}")
        raise

    updated_content = apply_replacements(original_content)

    if updated_content == original_content:
        print("未检测到需要写入的变更。")
        return

    diff = difflib.unified_diff(
        original_content.splitlines(keepends=True),
        updated_content.splitlines(keepends=True),
        fromfile="原始模板",
        tofile="替换后内容",
        lineterm="",
    )
    print("模板内容 diff 预览：")
    print("".join(list(diff)[:20]))

    try:
        write_file(template_path, updated_content)
    except Exception as exc:
        print(f"写入模板失败：{exc}")
        raise

    restart_container("docker-nginx-1")
    print("Nginx container restarted with updated configuration.")


if __name__ == "__main__":
    main()