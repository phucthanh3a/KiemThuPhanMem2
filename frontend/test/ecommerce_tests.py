import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains # Thêm import này
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uuid

# Cấu hình cơ bản
BASE_URL = "https://e-commerce-for-testing.onrender.com"
WAIT_TIMEOUT = 10

@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# Test Case 1: Đăng ký với dữ liệu hợp lệ và chỉ dừng lại ở thông báo thành công
def test_register_only_with_valid_data(driver): # Đổi tên hàm để rõ ràng hơn
    print("\n--- Test Case 1: Đăng ký với dữ liệu hợp lệ và kiểm tra thông báo thành công ---")
    driver.get(BASE_URL)

    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    register_nav_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//a[@href="/signup"]/button[text()="Register"]'))
    )
    register_nav_button.click()
    print("Đã click nút 'Register' trên Navbar.")

    wait.until(EC.url_contains("/signup"))
    wait.until(EC.presence_of_element_located((By.NAME, "email")))

    # Dữ liệu đăng ký
    register_email = "user21@gmail.com" # Hoặc dùng f"user_{uuid.uuid4()}@gmail.com" để test nhiều lần
    register_password = "thanh123456"

    driver.find_element(By.NAME, "email").send_keys(register_email)
    driver.find_element(By.NAME, "password").send_keys(register_password)
    driver.find_element(By.NAME, "passwordConfirm").send_keys(register_password)
    print(f"Đã điền email: {register_email} và mật khẩu.")

    sign_up_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    sign_up_button.click()
    print("Đã click nút 'Sign Up'.")

    success_alert_locator = (By.CSS_SELECTOR, '.chakra-alert[status="success"]')
    try:
        success_alert = wait.until(EC.presence_of_element_located(success_alert_locator))
        alert_text = success_alert.text
        print(f"Thông báo thành công trên giao diện: {alert_text}")
        assert "Registration successful" in alert_text or "Đăng ký thành công" in alert_text, \
            f"Thông báo thành công không chứa nội dung mong đợi: {alert_text}"
        print("Xác nhận đăng ký thành công qua alert. Test Case 1 PASSED.")

        # --- Gán thông tin tài khoản để Test Case 2 có thể sử dụng ---
        pytest.register_email = register_email
        pytest.register_password = register_password

        # Không làm gì thêm, test case kết thúc tại đây

    except Exception as e:
        print(f"Không tìm thấy thông báo thành công hoặc có lỗi: {e}")
        error_alert_locator = (By.CSS_SELECTOR, '.chakra-alert[status="error"]')
        try:
            error_message = wait.until(EC.presence_of_element_located(error_alert_locator)).text
            print(f"Thông báo lỗi trên giao diện: {error_message}")
            pytest.fail(f"Đăng ký thất bại: {error_message}")
        except Exception:
            pytest.fail("Đăng ký thất bại và không có thông báo lỗi rõ ràng.")


# Test Case 2: Đăng nhập với dữ liệu hợp lệ và quay lại trang chủ
def test_login_and_return_to_home(driver): # Đổi tên hàm để rõ ràng hơn
    print("\n--- Test Case 2: Đăng nhập và quay lại trang chủ ---")
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # Lấy thông tin tài khoản từ Test Case 1 hoặc dùng mặc định
    login_email = "user21@gmail.com"  # <<< THAY THẾ BẰNG EMAIL CÓ SẴN TRONG DB CỦA BẠN
    login_password = "thanh123456"     # <<< THAY THẾ BẰNG PASSWORD CÓ SẴN TRONG DB CỦA BẠN

    try:
        if hasattr(pytest, 'register_email') and hasattr(pytest, 'register_password'):
            login_email = pytest.register_email
            login_password = pytest.register_password
            print("Sử dụng tài khoản từ test đăng ký trước đó.")
        else:
            print(f"Không tìm thấy tài khoản từ test đăng ký. Sử dụng tài khoản mặc định: {login_email}")
    except AttributeError:
        print(f"Không tìm thấy tài khoản từ test đăng ký. Sử dụng tài khoản mặc định: {login_email}")

    # Bước 1: Điều hướng đến trang giao diện chính (homepage)
    print(f"Điều hướng đến trang chủ: {BASE_URL}")
    driver.get(BASE_URL)

    # Bước 2: Đảm bảo đã đăng xuất trước khi đăng nhập
    try:
        profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "/profile")]')), timeout=3)
        profile_link.click()
        print("Đã click vào Profile để kiểm tra trạng thái đăng nhập.")

        logout_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Logout"]')), timeout=3)
        logout_button.click()
        wait.until(EC.url_to_be(f"{BASE_URL}/"), timeout=5)
        print('Đã đăng xuất thành công.')
    except Exception:
        print('Chưa đăng nhập hoặc không tìm thấy nút Logout. Tiếp tục.')

    # Bước 3: Click vào nút "Login" trên Navbar để đến trang đăng nhập
    print("Tìm và click nút 'Login' trên Navbar.")
    login_nav_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//a[@href="/signin"]/button[text()="Login"]'))
    )
    login_nav_button.click()
    print("Đã click nút 'Login' trên Navbar.")

    # Bước 4: Chờ các trường email và password xuất hiện trên trang đăng nhập
    wait.until(EC.url_contains("/signin"))
    wait.until(EC.presence_of_element_located((By.NAME, "email")))

    # Bước 5: Điền thông tin và đăng nhập
    driver.find_element(By.NAME, "email").send_keys(login_email)
    driver.find_element(By.NAME, "password").send_keys(login_password)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    print(f"Đã điền thông tin và click đăng nhập với email: {login_email}")

    # Bước 6: Chờ chuyển hướng đến trang Profile sau khi đăng nhập thành công
    wait.until(EC.url_contains("/profile"))
    print(f"Đăng nhập thành công với email: {login_email} và đã chuyển đến trang Profile.")

    # --- PHẦN MỚI: NHẤN VÀO BUTTON "Products" ĐỂ QUAY LẠI TRANG CHỦ ---
    print("Tìm và click nút 'Products' trên Navbar để quay lại trang chủ.")
    # Selector cho nút Products trên Navbar
    # Dựa vào cấu trúc Navbar, có thể là một Link với text "Products"
    products_nav_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//a[@href="/"]/button[text()="Products"]'))
        # Hoặc nếu nó là một Text thông thường không phải button:
        # EC.element_to_be_clickable((By.XPATH, '//a[@href="/"][text()="Products"]'))
    )
    products_nav_button.click()
    print("Đã click nút 'Products' trên Navbar.")

    # Bước 7: Chờ URL quay về trang chủ (BASE_URL/)
    wait.until(EC.url_to_be(f"{BASE_URL}/"))
    print("Đã quay lại trang chủ thành công. Test Case 2 PASSED.")

# ... (GIỮ NGUYÊN test_add_product_to_cart và test_remove_product_from_cart)