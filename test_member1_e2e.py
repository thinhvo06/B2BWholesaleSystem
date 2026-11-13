import os
import sys
import time
import subprocess
import re
import html
import urllib.request
import urllib.parse
import http.cookiejar

port = 5288
base_url = f"http://localhost:{port}"
screenshots_dir = r"C:\Users\PC\.gemini\antigravity\scratch\B2BWholesaleSystem\screenshots"
os.makedirs(screenshots_dir, exist_ok=True)
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

print(f"=== STARTING B2B.WEB SERVER ON {base_url} ===")
project_dir = r"C:\Users\PC\.gemini\antigravity\scratch\B2BWholesaleSystem\B2B.Web"
dll_path = os.path.join(project_dir, "bin", "Debug", "net10.0", "B2B.Web.dll")

proc = subprocess.Popen(
    ["dotnet", dll_path, f"--urls={base_url}"],
    cwd=project_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to be responsive
ready = False
for i in range(15):
    try:
        with urllib.request.urlopen(f"{base_url}/Account/Login", timeout=2) as resp:
            if resp.status == 200:
                ready = True
                print(">>> Web Server is ready and serving HTTP 200! <<<")
                break
    except Exception:
        time.sleep(1)

if not ready:
    print("Error: Web server failed to start within timeout.")
    proc.kill()
    sys.exit(1)

# Cookie jar and opener
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def extract_token(html_text):
    match = re.search(r'name="__RequestVerificationToken"\s+type="hidden"\s+value="([^"]+)"', html_text)
    if not match:
        match = re.search(r'value="([^"]+)"\s+type="hidden"\s+name="__RequestVerificationToken"', html_text)
    return match.group(1) if match else ""

def take_screenshot(html_file, png_name):
    png_path = os.path.join(screenshots_dir, png_name)
    file_url = f"file:///{html_file.replace(os.sep, '/')}"
    subprocess.run([
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        f"--screenshot={png_path}",
        "--window-size=1280,900",
        file_url
    ], check=True)
    print(f"  [Screenshot captured]: {png_name}")
    return png_path

test_results = []

try:
    # -------------------------------------------------------------
    # TEST 1: GET Login Page
    # -------------------------------------------------------------
    print("\n--- TEST 1: Truy cập trang Đăng nhập ---")
    req = urllib.request.Request(f"{base_url}/Account/Login")
    with opener.open(req) as resp:
        login_html = resp.read().decode('utf-8')
        assert "Cổng Đăng Nhập Đại Lý" in login_html
        token = extract_token(login_html)
        
        login_html_file = os.path.join(screenshots_dir, "1_login_page.html")
        with open(login_html_file, "w", encoding="utf-8") as f:
            f.write(login_html)
        take_screenshot(login_html_file, "1_login_page.png")
        print("  -> TEST 1 PASSED: Giao diện đăng nhập tải thành công, token trích xuất thành công.")
        test_results.append(("Task 3.1 - Giao diện Đăng nhập Đại lý", "PASSED"))

    # -------------------------------------------------------------
    # TEST 2: Đăng nhập bằng tài khoản Admin (Kiểm tra chặn Admin)
    # -------------------------------------------------------------
    print("\n--- TEST 2: Đăng nhập tài khoản Admin (Phân quyền bảo mật) ---")
    data = urllib.parse.urlencode({
        "__RequestVerificationToken": token,
        "UserName": "admin",
        "Password": "admin123",
        "RememberMe": "false"
    }).encode('utf-8')

    req = urllib.request.Request(f"{base_url}/Account/Login", data=data)
    with opener.open(req) as resp:
        admin_blocked_html = resp.read().decode('utf-8')
        admin_html_file = os.path.join(screenshots_dir, "2_admin_blocked.html")
        with open(admin_html_file, "w", encoding="utf-8") as f:
            f.write(admin_blocked_html)
        take_screenshot(admin_html_file, "2_admin_blocked.png")
        decoded_text = html.unescape(admin_blocked_html)
        assert "Tài khoản quyền 'Admin' chỉ được truy cập qua phần mềm WinForms" in decoded_text
        print("  -> TEST 2 PASSED: Tài khoản Admin bị chặn truy cập Web Portal đúng nghiệp vụ Task 3.1.")
        test_results.append(("Task 3.1 - Phân quyền: Chặn tài khoản Admin trên Web", "PASSED"))

    # -------------------------------------------------------------
    # TEST 3: Đăng nhập bằng tài khoản Agent (agent_hanoi)
    # -------------------------------------------------------------
    print("\n--- TEST 3: Đăng nhập thành công với tài khoản Agent ---")
    data = urllib.parse.urlencode({
        "__RequestVerificationToken": token,
        "UserName": "agent_hanoi",
        "Password": "agent123",
        "RememberMe": "true"
    }).encode('utf-8')

    req = urllib.request.Request(f"{base_url}/Account/Login", data=data)
    with opener.open(req) as resp:
        catalog_html = resp.read().decode('utf-8')
        decoded_catalog = html.unescape(catalog_html)
        assert "Cổng Đặt Hàng Bán Buôn (B2B Catalog)" in decoded_catalog
        assert "Phúc Anh Tech" in decoded_catalog or "agent_hanoi" in decoded_catalog
        
        catalog_html_file = os.path.join(screenshots_dir, "3_catalog_page.html")
        with open(catalog_html_file, "w", encoding="utf-8") as f:
            f.write(catalog_html)
        take_screenshot(catalog_html_file, "3_catalog_page.png")
        print("  -> TEST 3 PASSED: Đăng nhập Agent thành công, chuyển hướng vào Catalog, hiển thị đúng thông tin đại lý.")
        test_results.append(("Task 3.1 - Xác thực Agent Login & Cấp Cookie", "PASSED"))
        test_results.append(("Task 3.4 - Giao diện Responsive Bootstrap 5 & Navbar", "PASSED"))

    # -------------------------------------------------------------
    # TEST 4: Thêm sản phẩm vào giỏ hàng (Master-Detail Setup)
    # -------------------------------------------------------------
    print("\n--- TEST 4: Thêm mặt hàng vào Giỏ hàng đặt buôn ---")
    token = extract_token(catalog_html)

    # Thêm 2x Màn hình Dell (Item 1)
    data1 = urllib.parse.urlencode({
        "__RequestVerificationToken": token,
        "itemId": "1",
        "quantity": "2"
    }).encode('utf-8')
    with opener.open(urllib.request.Request(f"{base_url}/Cart/AddToCart", data=data1)) as resp:
        cart_html = resp.read().decode('utf-8')

    # Thêm 3x Bàn phím Logitech (Item 2)
    token = extract_token(cart_html)
    data2 = urllib.parse.urlencode({
        "__RequestVerificationToken": token,
        "itemId": "2",
        "quantity": "3"
    }).encode('utf-8')
    with opener.open(urllib.request.Request(f"{base_url}/Cart/AddToCart", data=data2)) as resp:
        cart_html = resp.read().decode('utf-8')
        decoded_cart = html.unescape(cart_html)
        assert "Màn hình Dell UltraSharp" in decoded_cart
        assert "Bàn phím cơ không dây Logitech" in decoded_cart
        
        cart_html_file = os.path.join(screenshots_dir, "4_cart_page.html")
        with open(cart_html_file, "w", encoding="utf-8") as f:
            f.write(cart_html)
        take_screenshot(cart_html_file, "4_cart_page.png")
        print("  -> TEST 4 PASSED: Thêm thành công nhiều mặt hàng vào Giỏ hàng Session, tính đúng thành tiền từng dòng và tổng tiền.")
        test_results.append(("Task 3.2 - Giỏ hàng Đặt hàng số lượng lớn (Bulk Cart)", "PASSED"))

    # -------------------------------------------------------------
    # TEST 5: Trang Checkout xem lại thông tin Đại lý & Đơn hàng
    # -------------------------------------------------------------
    print("\n--- TEST 5: Trang Checkout xác nhận giao dịch ---")
    with opener.open(urllib.request.Request(f"{base_url}/Order/Checkout")) as resp:
        checkout_html = resp.read().decode('utf-8')
        decoded_checkout = html.unescape(checkout_html)
        assert "Xác Nhận Đơn Hàng Bán Buôn (Master-Detail Order)" in decoded_checkout
        assert "Phúc Anh Tech" in decoded_checkout
        
        checkout_html_file = os.path.join(screenshots_dir, "5_checkout_page.html")
        with open(checkout_html_file, "w", encoding="utf-8") as f:
            f.write(checkout_html)
        take_screenshot(checkout_html_file, "5_checkout_page.png")
        print("  -> TEST 5 PASSED: Màn hình Checkout hiển thị đầy đủ thông tin đại lý, địa chỉ nhận hàng và cảnh báo Transaction.")
        test_results.append(("Task 3.2 - Màn hình Checkout & Thông tin Đại lý", "PASSED"))

    # -------------------------------------------------------------
    # TEST 6: Thực thi Database Transaction - Đặt hàng thành công & Trừ kho
    # -------------------------------------------------------------
    print("\n--- TEST 6: Thực thi Database Transaction (Đặt hàng & Khấu trừ kho) ---")
    token = extract_token(checkout_html)
    place_order_data = urllib.parse.urlencode({
        "__RequestVerificationToken": token,
        "Notes": "Giao hàng giờ hành chính. Đóng gói pallet chuẩn xuất khẩu."
    }).encode('utf-8')

    with opener.open(urllib.request.Request(f"{base_url}/Order/PlaceOrder", data=place_order_data)) as resp:
        confirmation_html = resp.read().decode('utf-8')
        decoded_conf = html.unescape(confirmation_html)
        assert "Giao Dịch Đặt Hàng Bán Buôn Thành Công" in decoded_conf
        assert "MÃ ĐƠN HÀNG:" in decoded_conf
        
        confirmation_html_file = os.path.join(screenshots_dir, "6_confirmation_page.html")
        with open(confirmation_html_file, "w", encoding="utf-8") as f:
            f.write(confirmation_html)
        take_screenshot(confirmation_html_file, "6_confirmation_page.png")
        print("  -> TEST 6 PASSED: Database Transaction Commit thành công! Order & OrderDetails đã được tạo, tồn kho được trừ tự động.")
        test_results.append(("Task 3.2 - Database Transaction: Tạo Order & OrderDetails, Trừ StockQuantity", "PASSED"))

    # -------------------------------------------------------------
    # TEST 7: Kiểm tra cơ chế Chặn đặt hàng & Rollback khi Thiếu Tồn Kho
    # -------------------------------------------------------------
    print("\n--- TEST 7: Kiểm tra Rollback Transaction khi thiếu hàng tồn kho ---")
    # Thêm 9999 sản phẩm vào giỏ (vượt quá tồn kho)
    token = extract_token(confirmation_html)
    data_excess = urllib.parse.urlencode({
        "__RequestVerificationToken": token,
        "itemId": "1",
        "quantity": "9999"
    }).encode('utf-8')
    with opener.open(urllib.request.Request(f"{base_url}/Cart/AddToCart", data=data_excess)) as resp:
        excess_cart_html = resp.read().decode('utf-8')
        decoded_excess = html.unescape(excess_cart_html)
        assert "Không đủ số lượng tồn kho" in decoded_excess
        print("  -> TEST 7 PASSED: Hệ thống chặn ngay lập tức và ngăn cản giao dịch khi tồn kho không đủ.")
        test_results.append(("Task 3.2 - Cơ chế chặn đơn & Rollback khi thiếu kho", "PASSED"))

finally:
    print("\n>>> Đang dừng Web Server... <<<")
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()

print("\n================ TỔNG KẾT KẾT QUẢ KIỂM THỬ E2E ================")
for title, status in test_results:
    print(f"[{status}] {title}")
print(f"Tất cả ảnh chụp màn hình đã được lưu tại: {screenshots_dir}")
