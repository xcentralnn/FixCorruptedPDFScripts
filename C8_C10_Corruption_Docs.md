# Tài liệu Chuyên môn: Các Kịch bản Lỗi Cấu trúc tệp PDF (C8 - C10)

Tài liệu này cung cấp cái nhìn toàn diện về ba kịch bản gây lỗi trên định dạng PDF (C8-C10) thuộc bộ kiểm thử REPDF. Các kịch bản được phân tích dưới góc độ kỹ thuật chuyên sâu, đồng thời kèm theo các diễn giải trực quan để đảm bảo tính dễ tiếp cận cho mọi đối tượng.

---

## C8: Font Resources Deletion (Xóa tài nguyên phông chữ)

- **Mô tả kỹ thuật**: Kịch bản này phá vỡ tính toàn vẹn của các tài nguyên phông chữ (font) được nhúng (embedded) bên trong tài liệu PDF.
- **Diễn giải trực quan**: Giống như việc bạn gửi một bức thư được viết bằng "mật mã" nhưng lại bỏ sót "bảng dịch mật mã". Người nhận sẽ thấy các ký tự nhưng không thể hiểu nội dung.
- **Cơ chế triển khai**: 
  - Trong cấu trúc PDF, phông chữ được lưu trữ dưới dạng các luồng dữ liệu (stream) được tham chiếu bởi các thẻ như `/FontFile2` (chứa dữ liệu TrueType/OpenType) và `/ToUnicode` (bảng ánh xạ ký tự sang mã Unicode chuẩn).
  - Kịch bản tiến hành định vị và xóa bỏ trực tiếp nội dung của hai luồng dữ liệu này.
- **Hệ quả quan sát được**: 
  - Quá trình kết xuất (rendering) của trình đọc PDF bị thất bại. Các ký tự hiển thị sai lệch, biến thành các khối vuông (tofu) hoặc hoàn toàn biến mất.
  - Vô hiệu hóa chức năng trích xuất dữ liệu: Người dùng không thể sao chép (copy) văn bản vì thiếu bảng ánh xạ Unicode.

## C9: Zlib Tampering (Làm sai lệch luồng nén Zlib)

- **Mô tả kỹ thuật**: Kịch bản này đánh giá khả năng chịu lỗi (fault tolerance) của trình đọc PDF đối với các sự cố giải mã luồng nén Zlib.
- **Diễn giải trực quan**: Giống như một túi đồ được hút chân không. Nếu có dù chỉ một vết thủng nhỏ bằng đầu kim, áp suất bị phá vỡ và túi không còn giữ được trạng thái nén nguyên vẹn.
- **Cơ chế triển khai**: 
  - Hầu hết nội dung thực tế (văn bản, hình ảnh, đồ họa) trong PDF được nén bằng thuật toán Zlib (biểu diễn qua bộ lọc `/FlateDecode`) và nằm giữa các thẻ `stream` - `endstream`.
  - Kịch bản thực hiện việc thay đổi giá trị (bit-flip) của đúng một điểm dữ liệu (1 byte) ngẫu nhiên nằm bên trong vùng dữ liệu nén này.
- **Hệ quả quan sát được**: 
  - Thuật toán Zlib không vượt qua được bước kiểm tra toàn vẹn (checksum validation). Trình đọc PDF sẽ báo lỗi ngoại lệ giải mã (decoding exception).
  - Tùy thuộc vào trình duyệt, toàn bộ nội dung của trang hoặc hình ảnh tương ứng với luồng dữ liệu bị lỗi sẽ bị bỏ qua và không được hiển thị.

## C10: Partial Truncation (Cắt xén cấu trúc tệp)

- **Mô tả kỹ thuật**: Kịch bản này mô phỏng sự cố thiếu hụt dữ liệu cấu trúc cốt lõi do truyền tải mạng gián đoạn hoặc lỗi truy xuất bộ nhớ vật lý.
- **Diễn giải trực quan**: Giống như việc bạn đang đọc một cuốn sách nhưng bị xé mất 30% số trang cuối. Vấn đề nghiêm trọng nhất là phần "Mục lục" của cuốn sách lại luôn được in ở trang cuối cùng.
- **Cơ chế triển khai**: 
  - Tệp PDF bị cắt xén một cách vật lý: 30% dung lượng ở phần cuối của tệp bị loại bỏ hoàn toàn, chỉ bảo toàn 70% dữ liệu tính từ vị trí bắt đầu (Header).
- **Hệ quả quan sát được**: 
  - Trong đặc tả cấu trúc định dạng PDF, bảng tham chiếu chéo (XRef table) - nơi lưu trữ vị trí của toàn bộ các đối tượng - và cấu trúc Trailer luôn nằm ở cuối tệp.
  - Việc mất XRef table khiến trình đọc PDF mất phương hướng định tuyến đối tượng. Đa số trình đọc sẽ báo lỗi tệp hỏng cục bộ (corrupted) và từ chối xử lý. Các trình đọc nâng cao có cơ chế tự phục hồi (auto-rebuild) vẫn sẽ thất thoát vĩnh viễn nội dung chứa trong 30% dữ liệu đã bị cắt.
