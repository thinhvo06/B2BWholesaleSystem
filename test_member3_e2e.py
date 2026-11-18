import os
import sys
import time
import subprocess
import re
import html
import urllib.request
import urllib.parse
import http.cookiejar
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "B2B.Web")
TESTS_PROJ = os.path.join(BASE_DIR, "B2B.Tests", "B2B.Tests.csproj")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

DOTNET = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "dotnet10", "dotnet.exe")
if not os.path.exists(DOTNET):
    DOTNET = "dotnet"

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 5290
BASE_URL = f"http://localhost:{PORT}"


def extract_token(html_text: str) -> str:
    m = re.search(r'name="__RequestVerificationToken"\s+type="hidden"\s+value="([^"]+)"', html_text)
    if not m:
        m = re.search(r'value="([^"]+)"\s+type="hidden"\s+name="__RequestVerificationToken"', html_text)
    return m.group(1) if m else ""


def capture_html_png(html_content: str, html_name: str, png_name: str, width: int = 1280, height: int = 960):
    html_path = os.path.join(SCREENSHOTS_DIR, html_name)
    png_path = os.path.join(SCREENSHOTS_DIR, png_name)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    file_url = "file:///" + html_path.replace("\\", "/")
    subprocess.run([
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--screenshot={png_path}",
        f"--window-size={width},{height}",
        "--virtual-time-budget=4000",
        file_url
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  [Screenshot] {png_name} ({width}x{height})")
    return html_path, png_path


def capture_html_pdf(html_path: str, pdf_name: str):
    pdf_path = os.path.join(SCREENSHOTS_DIR, pdf_name)
    file_url = "file:///" + html_path.replace("\\", "/")
    subprocess.run([
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        "--virtual-time-budget=4000",
        file_url
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  [PDF Print]  {pdf_name}")
    return pdf_path


def render_unit_test_screenshot(test_output: str, png_name: str = "unit_test_results.png"):
    lines = [
        "PS C:\\B2BWholesaleSystem> dotnet test B2B.Tests/B2B.Tests.csproj --logger \"console;verbosity=detailed\"",
        ""
    ]
    for raw in test_output.splitlines():
        line = raw.rstrip()
        if line.startswith("Test run for") or "[xUnit.net" in line or line.strip().startswith("Passed ") or \
           line.strip().startswith("Failed ") or "Test Run Successful" in line or \
           "Total tests:" in line or "Passed:" in line or "Total time:" in line:
            lines.append(line)

    # Render clean dark-theme terminal image
    font_path = r"C:\Windows\Fonts\consola.ttf"
    font_bold_path = r"C:\Windows\Fonts\consolab.ttf"
    font = ImageFont.truetype(font_path, 13) if os.path.exists(font_path) else ImageFont.load_default()
    font_bold = ImageFont.truetype(font_bold_path, 15) if os.path.exists(font_bold_path) else font

    width = 1480
    line_height = 22
    padding = 24
    header_h = 44
    height = header_h + padding * 2 + line_height * len(lines) + 20

    img = Image.new("RGB", (width, height), (24, 28, 36))
    draw = ImageDraw.Draw(img)

    # Window title bar
    draw.rectangle([(0, 0), (width, header_h)], fill=(36, 42, 54))
    draw.ellipse([(16, 15), (30, 29)], fill=(255, 95, 86))
    draw.ellipse([(38, 15), (52, 29)], fill=(255, 189, 46))
    draw.ellipse([(60, 15), (74, 29)], fill=(39, 201, 63))
    draw.text((95, 13), "xUnit Test Runner - B2B.Tests (.NET 10.0 | Relational SQLite In-Memory) - 16/16 PASSED", fill=(220, 228, 240), font=font_bold)

    y = header_h + padding
    for line in lines:
        color = (220, 226, 236)
        if line.startswith("PS "):
            color = (102, 217, 239)
        elif line.strip().startswith("Passed "):
            color = (126, 231, 135)
        elif "Test Run Successful" in line or "Passed:" in line or "Total tests:" in line:
            color = (86, 211, 100)
        elif "[xUnit.net" in line:
            color = (180, 190, 210)
        draw.text((padding, y), line[:195], fill=color, font=font)
        y += line_height

    out_path = os.path.join(SCREENSHOTS_DIR, png_name)
    img.save(out_path)
    print(f"  [Screenshot] {png_name} ({width}x{height})")


def main():
    # 1. Run Unit Tests & Capture Real Output Screenshot
    print("=== 1. RUNNING UNIT TESTS (B2B.Tests) ===")
    test_proc = subprocess.run(
        [DOTNET, "test", TESTS_PROJ, "--logger", "console;verbosity=detailed", "--nologo"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if test_proc.returncode != 0:
        print(test_proc.stdout)
        print(test_proc.stderr)
        sys.exit(1)
    assert "Total tests: 16" in test_proc.stdout and "Passed: 16" in test_proc.stdout
    print("  -> Unit Tests PASSED: 16/16 (100%)")
    render_unit_test_screenshot(test_proc.stdout, "unit_test_results.png")

    # 2. Build & Launch B2B.Web
    print("\n=== 2. STARTING B2B.WEB SERVER ===")
    subprocess.run([DOTNET, "build", os.path.join(WEB_DIR, "B2B.Web.csproj"), "--nologo"], check=True, stdout=subprocess.DEVNULL)
    dll_path = os.path.join(WEB_DIR, "bin", "Debug", "net10.0", "B2B.Web.dll")
    proc = subprocess.Popen(
        [DOTNET, dll_path, f"--urls={BASE_URL}"],
        cwd=WEB_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    ready = False
    for _ in range(20):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/Account/Login", timeout=2) as r:
                if r.status == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(0.7)

    if not ready:
        proc.kill()
        print("ERROR: B2B.Web failed to start!")
        sys.exit(1)
    print(f"  -> B2B.Web running at {BASE_URL}")

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    try:
        # Login as agent_hanoi (AgentID = 1)
        with opener.open(f"{BASE_URL}/Account/Login") as resp:
            login_html = resp.read().decode("utf-8")
        token = extract_token(login_html)

        login_data = urllib.parse.urlencode({
            "__RequestVerificationToken": token,
            "UserName": "agent_hanoi",
            "Password": "agent123",
            "RememberMe": "true"
        }).encode("utf-8")
        with opener.open(urllib.request.Request(f"{BASE_URL}/Account/Login", data=login_data)) as resp:
            _ = resp.read().decode("utf-8")
        print("  -> Logged in as agent_hanoi (AgentID=1)")

        # Task 3.3 Check 1: My Orders Page
        with opener.open(f"{BASE_URL}/Order/MyOrders") as resp:
            my_orders_html = resp.read().decode("utf-8")
            decoded = html.unescape(my_orders_html)
            assert "Lịch Sử Đơn Hàng Đại Lý (My Orders)" in decoded
            assert "Phúc Anh Tech" in decoded
            assert "#1" in decoded and "#6" in decoded
            # Ensure Agent 2's orders (#2, #7, #15) are NOT leaked into Agent 1's list
            assert "Phong Vũ Mega" not in decoded
        capture_html_png(my_orders_html, "7_my_orders_page.html", "7_my_orders_page.png", 1280, 920)
        capture_html_png(my_orders_html, "7_my_orders_page.html", "11_my_orders_mobile.png", 390, 844)
        print("  -> Verified My Orders (Agent 1 sees ONLY own orders #1 and #6)")

        # Task 3.3 Check 2: Printable Invoice View (Order #1 owned by Agent 1)
        with opener.open(f"{BASE_URL}/Order/Invoice/1") as resp:
            invoice_html = resp.read().decode("utf-8")
            decoded_inv = html.unescape(invoice_html)
            assert "HÓA ĐƠN BÁN BUÔN" in decoded_inv
            assert "B2B WHOLESALE DISTRIBUTION CORP." in decoded_inv
            assert "Phúc Anh Tech" in decoded_inv
            assert "Màn hình Dell UltraSharp 27 inch 4K" in decoded_inv
            assert "In Hóa Đơn / Xuất PDF" in decoded_inv
        inv_html_path, _ = capture_html_png(invoice_html, "8_invoice_page.html", "8_invoice_page.png", 1280, 1280)
        capture_html_pdf(inv_html_path, "9_invoice_print_a4.pdf")
        print("  -> Verified Printable Invoice #1 + generated A4 Print-Media PDF")

        # Task 3.3 Check 3: IDOR Protection (Agent 1 attempts to access Agent 2's Order #2)
        with opener.open(f"{BASE_URL}/Order/Invoice/2") as resp:
            idor_html = resp.read().decode("utf-8")
            decoded_idor = html.unescape(idor_html)
            assert "không có quyền truy cập đơn hàng của đại lý khác" in decoded_idor
            assert "HÓA ĐƠN BÁN BUÔN" not in decoded_idor
        capture_html_png(idor_html, "10_my_orders_idor_blocked.html", "10_my_orders_idor_blocked.png", 1280, 820)
        print("  -> Verified IDOR Protection: Agent 1 blocked from accessing Agent 2's Order #2!")

        print("\n=== ALL MEMBER 3 E2E VERIFICATIONS PASSED 100%! ===")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
