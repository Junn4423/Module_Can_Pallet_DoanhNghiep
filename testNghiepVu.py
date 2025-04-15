import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import qrcode
from PIL import Image, ImageTk
import serial
import threading
import os
import re

# ===== Kết nối COM2 để nhận dữ liệu từ COM1 =====
ser = None
def connect_com():
    global ser
    try:
        ser = serial.Serial('COM2', 9600, timeout=1)
    except serial.SerialException as e:
        messagebox.showerror("Lỗi", f"Không thể kết nối COM2: {e}")

# ===== Tạo batch ID =====
def tao_batch_id():
    return datetime.now().strftime("%Y%m%d%H%M%S")

# ======= Hàm tính toán và tạo mã QR =======
def xu_ly_du_lieu():
    try:
        batch_id = tao_batch_id()
        thuc_str = entry_thuc.get()
        match = re.search(r"[\d\.]+", thuc_str)
        if not match:
            raise ValueError("Dữ liệu không hợp lệ")
        thuc = float(match.group())

        dong_goi = float(entry_dong_goi.get()) if entry_dong_goi.get() else 0
        tong = thuc + dong_goi
        thoigian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        qr_data = (
            f"Batch ID: {batch_id}\n"
            f"Khối lượng thực: {thuc} kg\n"
            f"Khối lượng đóng gói: {dong_goi} kg\n"
            f"Tổng khối lượng: {tong} kg\n"
            f"Thời gian cân: {thoigian}"
        )

        ket_qua.set(qr_data)

        qr = qrcode.make(qr_data)
        qr_filename = f"qr_{batch_id}.png"
        qr.save(qr_filename)

        img = Image.open(qr_filename).resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        label_qr.config(image=img_tk)
        label_qr.image = img_tk

    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi xử lý dữ liệu: {e}")

# ===== Đọc dữ liệu liên tục từ COM2 và hiển thị lên ô nhập =====
def read_com():
    while True:
        if ser and ser.in_waiting:
            try:
                data = ser.readline().decode().strip()
                if data:
                    entry_thuc.delete(0, tk.END)
                    entry_thuc.insert(0, data)
            except Exception as e:
                print("Lỗi đọc COM:", e)

# ======= Giao diện =======
root = tk.Tk()
root.title("Phần mềm cân pallet")

tk.Label(root, text="Khối lượng thực (kg):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
entry_thuc = tk.Entry(root)
entry_thuc.grid(row=0, column=1)

tk.Label(root, text="Khối lượng đóng gói (kg):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
entry_dong_goi = tk.Entry(root)
entry_dong_goi.grid(row=1, column=1)

tk.Button(root, text="Tính toán & In mã QR", command=xu_ly_du_lieu).grid(row=2, columnspan=2, pady=10)

ket_qua = tk.StringVar()
tk.Label(root, textvariable=ket_qua, justify="left", fg="blue").grid(row=3, columnspan=2, padx=5, pady=10)

label_qr = tk.Label(root)
label_qr.grid(row=4, columnspan=2, pady=10)

# ======= Kết nối COM và chạy thread đọc =======
connect_com()
threading.Thread(target=read_com, daemon=True).start()

root.mainloop()
