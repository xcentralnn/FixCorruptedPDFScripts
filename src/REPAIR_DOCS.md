# Hướng dẫn Kiểm thử: Mô phỏng lỗi và Phục hồi cấu trúc PDF (C8-C10)

Hệ thống được chia thành 3 thư mục chính để quản lý vòng đời kiểm thử chuyên nghiệp:

## 1. Thành phần Dự án
- **Thư mục `src/`**: Chứa toàn bộ mã nguồn mô phỏng và phục hồi lỗi.
  - Mô phỏng lỗi: `simulate_c8.py`, `simulate_c9.py`, `simulate_c10.py`
  - Khôi phục lỗi: `repair_c8.py`, `repair_c9.py`, `repair_c10.py`
- **Thư mục `input/`**: Chứa dữ liệu đầu vào.
  - Dữ liệu chuẩn: `demo_input.pdf` (Một file PDF hợp lệ lấy từ kho dữ liệu gốc).
- **Thư mục `output/`**: Chứa các tệp kết quả.
  - File lỗi (Demo): `demo_c8.pdf`, `demo_c9.pdf`, `demo_c10.pdf`
  - File đã sửa: `repaired_c8.pdf`, `repaired_c9.pdf`, `repaired_c10.pdf`

---

## 2. Giải phẫu thuật toán Phục hồi (Repair Algorithms)

### C8: Sửa lỗi mất phông chữ (`repair_c8.py`)
- **Cơ chế hoạt động**: Trong thực tiễn, việc phục hồi C8 phụ thuộc vào kho dữ liệu phông chữ ánh xạ ngoài. Script `repair_c8.py` cung cấp bản vá lỗi cấu trúc (structural patch): Rà quét và tái cấu trúc lại các tham chiếu `/FontFile2` bị hỏng, ngăn chặn trình xử lý PDF rơi vào trạng thái treo vô hạn. Nhờ đó, trình xử lý buộc phải hạ cấp xuống sử dụng các phông chữ có sẵn trên hệ điều hành (Fallback System Fonts).

### C9: Sửa lỗi Zlib Tampering (`repair_c9.py`)
- **Cơ chế hoạt động**: Sử dụng thuật toán **Brute-force Cryptanalysis** trên luồng dữ liệu. Hệ thống tự động dò tìm các khối dữ liệu Zlib bị lỗi (kiểm tra signature `0x78`). Tiếp theo, script lặp qua hàng ngàn tổ hợp để lật đảo giá trị của các byte bị nghi ngờ cho đến khi thuật toán zlib-decompress khớp thành công. Điểm đứt gãy được tái lập toàn vẹn ở mức độ bit.

### C10: Sửa lỗi đứt gãy đuôi tệp (`repair_c10.py`)
- **Cơ chế hoạt động**: Khai thác tính năng Tái thiết lập quan hệ đối tượng. Với 30% dữ liệu bị mất ở đuôi tệp (bao gồm XRef table và Trailer), script tiến hành quét toàn bộ các đối tượng mồ côi còn sót lại, sau đó xây dựng lại Page Tree và trỏ XRef table mới về các đối tượng này. Nhờ đó trình đọc có thể mở được các trang may mắn không bị mất phần `/Contents`.

---

## 3. Quy trình Triển khai Kiểm thử (Demo)

Mở Terminal / Command Prompt và điều hướng vào thư mục `src/`.

### Bước 1: Gây lỗi toàn diện
Khởi chạy bộ sinh lỗi để phá vỡ cấu trúc tệp chuẩn:
```bash
python simulate_c8.py
python simulate_c9.py
python simulate_c10.py
```
*(Hệ thống sẽ tự động đọc `demo_input.pdf` từ thư mục `input/` và kết xuất ra 3 tệp hỏng vào thư mục `output/`)*

### Bước 2: Kích hoạt khôi phục
Gọi các công cụ phục hồi tương ứng lên các tệp đã hỏng:
```bash
python repair_c8.py
python repair_c9.py
python repair_c10.py
```
*(Hệ thống sẽ lấy file hỏng từ thư mục `output/`, sửa chữa và xuất ra các tệp đã vá cấu trúc `repaired_*.pdf` cũng tại thư mục `output/`)*
