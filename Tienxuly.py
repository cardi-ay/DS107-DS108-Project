import os
import hashlib

def hash_file(path):
    """Tạo mã hash duy nhất cho nội dung file"""
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def remove_duplicate_files(folder):
    hashes = {}
    removed = 0

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            file_hash = hash_file(filepath)
            if file_hash in hashes:
                print(f"🗑️ Xóa bản trùng: {filename}")
                os.remove(filepath)
                removed += 1
            else:
                hashes[file_hash] = filename

    print(f"✅ Đã xóa {removed} file trùng lặp.")

# 👉 Gọi hàm
remove_duplicate_files("downloads")  # đổi tên thư mục nếu bạn dùng thư mục khác
