from __future__ import annotations
import re
import os
import subprocess
from datetime import datetime, timedelta
import json
import serial
from time import sleep, time

def main():
    subprocess.call(["clear"])
    while True:
        try:
            current_directory = os.getcwd()
            bottom_directory = os.path.basename(current_directory)
            # 標準入力を受け取り空白で分割する
            cmd = input(f"{bottom_directory} % ")
            cmd = list(filter(lambda x: x != '', re.split(r'[ 　]+', cmd)))
            process_cmd(cmd)
        except EOFError:
            # Ctrl + D で終了
            break

def process_cmd(cmd: str):
    try:
        if cmd[0] == "sudo" or cmd[0] == "git":
            if not previous_warning_check(cmd[0]):
                #まだアルコールが残っている
                try:
                    subprocess.call(["open", "https://superhotdogcat.github.io/BDM/"])
                except:
                    subprocess.call(["xdg-open", "https://superhotdogcat.github.io/BDM/"])
                exit()
            if not alcohol_check(cmd[0]):
                try:
                    subprocess.call(["open", "https://superhotdogcat.github.io/BDM/"])
                except:
                    subprocess.call(["xdg-open", "https://superhotdogcat.github.io/BDM/"])
                exit()
            else:
                subprocess.call(cmd)
        else:
            subprocess.call(cmd)
    except Exception as e:
        # 例外が発生したときにエラーメッセージを取得する
        error_message = str(e)
        print(error_message)

def alcohol_check(command: str):
    ser = serial.Serial('/dev/ttyACM0', 9600) #Aruduino Port
    threshold: int = 600
    FPS = 30
    SECOND_PER_FRAME = 1 / FPS # 1フレームにかかる時間
    SECOND = 5 #5秒間
    ALCOHOL_FLAG = True
    while SECOND > 0:
        start_time = time()
        data = int(ser.readline().decode("utf-8").strip().replace(" ", "").replace("A0:", ""))
        if data >= threshold:
            ALCOHOL_FLAG = False
        end_time = time()
        delta_time = end_time - start_time #経過時間
        SECOND -= delta_time #経過時間を引く
        sleep(max(0, SECOND_PER_FRAME - delta_time))
        print(f"検査終了まで残り: {int(SECOND)} 秒")
    if ALCOHOL_FLAG:
        return True
    elif not ALCOHOL_FLAG:
        warning_data = read_json_file()
        add_json_file(warning_data, command)
        return False

def read_json_file() -> list[dict]:
    with open('logs.json', 'r') as file:
        json_data = file.read()
    try:
        warning_data = json.loads(json_data)
    except:
        warning_data = []
    return warning_data

def add_json_file(warning_data: list[dict], command: str) -> None:
    warning_data.append({"command": command, "time": str(datetime.now())})
    with open('logs.json', 'w') as file:
        json.dump(warning_data, file, indent=4)

def write_json_file(warning_data: list[dict]) -> None:
    with open('logs.json', 'w') as file:
        json.dump(warning_data, file, indent=4)

def previous_warning_check(command: str):
    warning_data = read_json_file()
    for warning in warning_data:
        previous_command = warning["command"]
        previous_time = datetime.fromisoformat(warning["time"])
        current_time = datetime.now()
        if previous_command == command and current_time - previous_time < timedelta(hours=8):
            #まだアルコールが残っていると判定するため, Falseを返すことに
            return False
        if previous_command == command and current_time - previous_time >= timedelta(hours=8):
            #コマンドを実行しても良い
            warning_data.remove(warning) #8時間過ぎたデータは削除
            write_json_file(warning_data)
    return True

if __name__ == "__main__":
    main()