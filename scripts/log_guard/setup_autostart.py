#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

# Шаг 1: Перемещаем скрипт в /usr/local/bin/
script_name = "log_overflow_guard.py"
script_path = os.path.abspath(script_name)
dest_path = "/usr/local/bin/" + script_name

if not os.path.exists(dest_path):
    os.rename(script_path, dest_path)

# Шаг 2: Даем права на выполнение
os.chmod(dest_path, 0o755)

# Шаг 3: Создаем файл службы systemd
service_content = f"""[Unit]
Description=My Python Script

[Service]
ExecStart=/usr/local/bin/{script_name}
Restart=always
User=your_username
Group=your_groupname

[Install]
WantedBy=multi-user.target
"""

service_path = f"/etc/systemd/system/{script_name}.service"

with open(service_path, "w") as service_file:
    service_file.write(service_content)

# Шаг 4: Обновляем systemd
os.system("sudo systemctl daemon-reload")

# Шаг 5: Включаем службу
os.system(f"sudo systemctl enable {script_name}.service")

# Шаг 6: Запускаем службу
os.system(f"sudo systemctl start {script_name}.service")
