import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import qrcode
from PIL import Image, ImageTk
import serial
import threading
import os
import re

class PalletWeighingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phần Mềm Cân Pallet!")
        self.root.geometry("600x850")
        self.root.configure(bg="#f5f5f5")
        
        # Serial connection
        self.ser = None
        
        # Create UI
        self.create_ui()
        
        # Connect to COM port and start reading thread
        self.connect_com()
        threading.Thread(target=self.read_com, daemon=True).start()

    def create_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#3498db", height=100)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame, 
            text="PHẦN MỀM CÂN PALLET", 
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Main content
        content_frame = tk.Frame(self.root, bg="#f5f5f5", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Actual weight
        tk.Label(
            content_frame, 
            text="Khối lượng thực (kg):", 
            font=("Arial", 11),
            bg="#f5f5f5",
            anchor="w"
        ).pack(fill=tk.X, pady=(10, 5))
        
        self.entry_thuc = tk.Entry(content_frame, font=("Arial", 11))
        self.entry_thuc.pack(fill=tk.X, ipady=5)
        
        # Packaging weight
        tk.Label(
            content_frame, 
            text="Khối lượng đóng gói (kg):", 
            font=("Arial", 11),
            bg="#f5f5f5",
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_dong_goi = tk.Entry(content_frame, font=("Arial", 11))
        self.entry_dong_goi.pack(fill=tk.X, ipady=5)
        
        # Calculate button - FIXED: Using standard tk.Button with explicit styling
        self.calculate_button = tk.Button(
            content_frame,
            text="Tính Toán & In Mã QR",
            command=self.xu_ly_du_lieu,
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief=tk.RAISED,
            bd=1,
            padx=10,
            pady=8
        )
        self.calculate_button.pack(pady=20)
        
        # Results section
        result_frame = tk.LabelFrame(
            content_frame, 
            text="Kết Quả", 
            font=("Arial", 11, "bold"),
            bg="#f5f5f5",
            padx=10,
            pady=10
        )
        result_frame.pack(fill=tk.X, pady=10)
        
        self.ket_qua = tk.StringVar()
        self.result_label = tk.Label(
            result_frame,
            textvariable=self.ket_qua,
            justify="left",
            font=("Arial", 10),
            bg="#f5f5f5",
            anchor="w"
        )
        self.result_label.pack(fill=tk.X, pady=5)
        
        # QR code section
        qr_frame = tk.LabelFrame(
            content_frame, 
            text="Mã QR", 
            font=("Arial", 11, "bold"),
            bg="#f5f5f5",
            padx=10,
            pady=10
        )
        qr_frame.pack(fill=tk.X, pady=10)
        
        # FIXED: Create a frame with fixed size for QR code
        qr_container = tk.Frame(qr_frame, bg="#f5f5f5", width=200, height=200)
        qr_container.pack(pady=10)
        qr_container.pack_propagate(False)  # Prevent the frame from shrinking
        
        self.label_qr = tk.Label(qr_container, bg="#f5f5f5")
        self.label_qr.pack(expand=True, fill=tk.BOTH)
        
        # Default placeholder text
        self.label_qr.config(
            text="QR sẽ hiển thị ở đây",
            font=("Arial", 10),
            fg="#7f8c8d"
        )

    def connect_com(self):
        try:
            self.ser = serial.Serial('COM2', 9600, timeout=1)
        except serial.SerialException as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối COM2: {e}")

    def read_com(self):
        while True:
            if self.ser and self.ser.in_waiting:
                try:
                    data = self.ser.readline().decode().strip()
                    if data:
                        self.root.after(0, self.update_weight_entry, data)
                except Exception as e:
                    print("Lỗi đọc COM:", e)
    
    def update_weight_entry(self, data):
        self.entry_thuc.delete(0, tk.END)
        self.entry_thuc.insert(0, data)

    def tao_batch_id(self):
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def xu_ly_du_lieu(self):
        try:
            batch_id = self.tao_batch_id()
            thuc_str = self.entry_thuc.get()
            match = re.search(r"[\d\.]+", thuc_str)
            if not match:
                raise ValueError("Dữ liệu không hợp lệ")
            thuc = float(match.group())

            dong_goi = float(self.entry_dong_goi.get()) if self.entry_dong_goi.get() else 0
            tong = thuc + dong_goi
            thoigian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            qr_data = (
                f"Batch ID: {batch_id}\n"
                f"Khối lượng thực: {thuc} kg\n"
                f"Khối lượng đóng gói: {dong_goi} kg\n"
                f"Tổng khối lượng: {tong} kg\n"
                f"Thời gian cân: {thoigian}"
            )

            self.ket_qua.set(qr_data)

            # FIXED: Generate QR code with proper error handling
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_filename = f"qr_{batch_id}.png"
                qr_img.save(qr_filename)
                
                # FIXED: Properly display QR code
                img = Image.open(qr_filename).resize((180, 180))
                img_tk = ImageTk.PhotoImage(img)
                
                # Clear any text in the label before setting the image
                self.label_qr.config(text="")
                self.label_qr.config(image=img_tk)
                self.label_qr.image = img_tk  # Keep a reference to prevent garbage collection
                
                print(f"QR code generated and saved as {qr_filename}")
            except Exception as e:
                print(f"Error generating QR code: {e}")
                messagebox.showerror("Lỗi", f"Lỗi tạo mã QR: {e}")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý dữ liệu: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PalletWeighingApp(root)
    root.mainloop()
