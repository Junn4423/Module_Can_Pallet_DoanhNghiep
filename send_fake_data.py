# send_fake_data.py
import serial
import time
import random  # Thay vì math.random, sử dụng random

def send_fake_weight():
    ser = serial.Serial('COM1', 9600)  # Gửi ra COM1
    while True:
        fake_weight = random.uniform(0, 100)  # Sử dụng random để tạo số thực ngẫu nhiên
        ser.write(str(fake_weight).encode('utf-8'))  # Chuyển đổi fake_weight thành chuỗi và mã hóa thành bytes
        print(f"Đã gửi: {fake_weight}")
        time.sleep(2)  # gửi mỗi 2 giây

send_fake_weight()
