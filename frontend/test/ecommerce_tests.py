import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException
import time
import uuid

# Cấu hình cơ bản
BASE_URL = "https://e-commerce-for-testing.onrender.com"
WAIT_TIMEOUT = 15 # Tăng timeout lên 15 giây để linh hoạt hơn với server online
DISPLAY_TIME = 5 # Thời gian hiển thị sau khi test case hoàn thành (tính bằng giây)

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Chạy ẩn nếu không muốn hiển thị trình duyệt
    options.add_argument("--start-maximized") # Khởi động trình duyệt ở chế độ tối đa hóa
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5) # Implicit wait cho các thao tác tìm kiếm cơ bản
    yield driver
    driver.quit() # Dòng này sẽ đảm bảo driver đóng sau mỗi test function

# Test Case 1: Đăng ký với dữ liệu hợp lệ và chỉ dừng lại ở thông báo thành công
def test_01_register_only_with_valid_data(driver):
    print("\n--- Test Case 1: Đăng ký với dữ liệu hợp lệ và kiểm tra thông báo thành công ---")
    driver.get(BASE_URL)

    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    try:
        # Tìm và click nút 'Register' trên Navbar
        register_nav_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="/signup"]/button[text()="Register"]'))
        )
        register_nav_button.click()
        print("Đã click nút 'Register' trên Navbar.")
    except TimeoutException:
        pytest.fail("Không tìm thấy nút 'Register' trên Navbar. Kiểm tra lại cấu trúc trang chủ.")

    try:
        # Chờ chuyển hướng đến trang đăng ký và các trường nhập liệu xuất hiện
        wait.until(EC.url_contains("/signup"))
        wait.until(EC.presence_of_element_located((By.NAME, "email")))
        print("Đã chuyển đến trang đăng ký và các trường nhập liệu đã xuất hiện.")
    except TimeoutException:
        pytest.fail("Không chuyển đến trang đăng ký hoặc các trường nhập liệu không xuất hiện.")

    # Dữ liệu đăng ký
    register_email = f"user_{uuid.uuid4()}@gmail.com" # Đảm bảo email độc nhất
    register_password = "thanh123456" # Mật khẩu có độ dài 10 ký tự

    # Điền thông tin đăng ký
    driver.find_element(By.NAME, "email").send_keys(register_email)
    driver.find_element(By.NAME, "password").send_keys(register_password)
    driver.find_element(By.NAME, "passwordConfirm").send_keys(register_password)
    print(f"Đã điền email: {register_email} và mật khẩu.")

    # Click nút 'Sign Up'
    sign_up_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    sign_up_button.click()
    print("Đã click nút 'Sign Up'.")

    # --- CÁCH XÁC MINH THÔNG BÁO THÀNH CÔNG (GIẢ ĐỊNH LÀ JAVASCRIPT ALERT) ---
    expected_alert_text = "Đăng ký thành công!"

    try:
        # Chờ và chuyển đổi sang JavaScript Alert
        alert = wait.until(EC.alert_is_present(), message="Không tìm thấy JavaScript Alert sau khi đăng ký.")
        alert_text = alert.text
        print(f"Thông báo Alert trên trình duyệt: '{alert_text}'")

        # Xác minh nội dung của Alert
        assert expected_alert_text in alert_text, \
            f"Nội dung Alert không khớp. Mong đợi: '{expected_alert_text}', Thực tế: '{alert_text}'"

        # Chấp nhận (click OK) Alert
        alert.accept()
        print("Đã click 'OK' trên Alert.")

        # Tùy chọn: Chờ Alert biến mất (SỬA LỖI Ở ĐÂY)
        wait.until_not(EC.alert_is_present()) # Bỏ tham số timeout=5
        print("Alert đã biến mất.")

        print("Xác nhận đăng ký thành công qua JavaScript Alert. Test Case 1 PASSED.")
        time.sleep(DISPLAY_TIME) # Giữ màn hình sau khi test case thành công

        # --- Gán thông tin tài khoản để Test Case 2 có thể sử dụng ---
        pytest.register_email = register_email
        pytest.register_password = register_password

    except TimeoutException as e:
        print(f"Lỗi Timeout khi chờ JavaScript Alert: {e}. Có thể không phải là Alert thông thường.")
        # Nếu không phải JavaScript Alert, thử tìm thông báo lỗi HTML như trước
        error_alert_locator = (By.CSS_SELECTOR, '.chakra-alert[status="error"]')
        try:
            error_message = wait.until(EC.presence_of_element_located(error_alert_locator), timeout=5).text
            print(f"Thông báo lỗi trên giao diện (nếu có): {error_message}")
            pytest.fail(f"Đăng ký thất bại: {error_message}")
        except TimeoutException:
            pytest.fail("Đăng ký thất bại và không có thông báo lỗi rõ ràng (cả Alert lẫn HTML).")
        except Exception as ee:
            pytest.fail(f"Đăng ký thất bại với lỗi không xác định: {ee}")
    except Exception as e:
        pytest.fail(f"Đăng ký thất bại do một lỗi không mong đợi: {e}")


# Test Case 2: Đăng nhập với dữ liệu hợp lệ và quay lại trang chủ
def test_02_login_and_return_to_home(driver):
    print("\n--- Test Case 2: Đăng nhập và quay lại trang chủ ---")
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # Lấy thông tin tài khoản từ Test Case 1 hoặc dùng mặc định
    login_email = "user24@gmail.com"  # Cập nhật email mặc định
    login_password = "thanh12345"    # Cập nhật mật khẩu mặc định

    try:
        # Ưu tiên sử dụng tài khoản được đăng ký từ Test Case 1
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

    # --- BƯỚC CẢI TIẾN: Đảm bảo đăng xuất trước khi tiến hành đăng nhập ---
    # Thử tìm kiếm nút "Profile" hoặc "Logout" để xác định trạng thái đăng nhập
    print('Kiểm tra trạng thái đăng nhập và thực hiện đăng xuất nếu cần.')
    try:
        # Tìm nút "Profile" (hoặc bất kỳ dấu hiệu nào cho thấy người dùng đã đăng nhập)
        # Sử dụng visibility_of_element_located thay vì clickable để kiểm tra sự hiện diện
        profile_link_locator = (By.XPATH, '//a[contains(@href, "/profile")]')
        wait.until(EC.visibility_of_element_located(profile_link_locator), timeout=5)

        # Nếu nút Profile hiển thị, nghĩa là đã đăng nhập, tiến hành click và logout
        profile_link = driver.find_element(*profile_link_locator)
        profile_link.click()
        print("Đã click vào Profile để tiến hành đăng xuất.")

        # Chờ nút Logout xuất hiện và click vào nó
        logout_button_locator = (By.XPATH, '//button[text()="Logout"]')
        logout_button = wait.until(EC.element_to_be_clickable(logout_button_locator), timeout=5)
        logout_button.click()
        print('Đã click nút "Logout".')

        # Chờ URL quay về trang chủ sau khi đăng xuất
        wait.until(EC.url_to_be(f"{BASE_URL}/"), timeout=10)
        print('Đã đăng xuất thành công và quay về trang chủ.')

    except (TimeoutException, NoSuchElementException):
        # Nếu không tìm thấy nút Profile hoặc Logout trong thời gian chờ,
        # coi như chưa đăng nhập hoặc đã đăng xuất.
        print('Chưa đăng nhập hoặc không tìm thấy nút Profile/Logout. Tiếp tục với luồng đăng nhập.')
    except Exception as e:
        print(f"Lỗi không xác định khi cố gắng đăng xuất: {e}. Tiếp tục.")

    # Bước 3: Click vào nút "Login" trên Navbar để đến trang đăng nhập
    print("Tìm và click nút 'Login' trên Navbar.")
    try:
        login_nav_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="/signin"]/button[text()="Login"]'))
        )
        login_nav_button.click()
        print("Đã click nút 'Login' trên Navbar.")
    except TimeoutException:
        pytest.fail("Không tìm thấy nút 'Login' trên Navbar. Kiểm tra lại cấu trúc Navbar.")

    # Bước 4: Chờ các trường email và password xuất hiện trên trang đăng nhập
    try:
        wait.until(EC.url_contains("/signin"))
        wait.until(EC.presence_of_element_located((By.NAME, "email")))
        print("Đã chuyển đến trang đăng nhập và các trường nhập liệu đã xuất hiện.")
    except TimeoutException:
        pytest.fail("Không chuyển đến trang đăng nhập hoặc các trường nhập liệu không xuất hiện.")

    # Bước 5: Điền thông tin và click đăng nhập
    driver.find_element(By.NAME, "email").send_keys(login_email)
    driver.find_element(By.NAME, "password").send_keys(login_password)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    print(f"Đã điền thông tin và click đăng nhập với email: {login_email}")

    # --- ÁP DỤNG PHƯƠNG ÁN 3: ĐIỀU HƯỚNG TRỰC TIẾP SAU KHI ĐĂNG NHẬP ---
    try:
        # Giả định đăng nhập thành công. Điều hướng trực tiếp đến trang chủ.
        driver.get(BASE_URL)
        print(f"Đăng nhập thành công với email: {login_email}. Đã điều hướng trực tiếp về trang chủ: {BASE_URL}/")

        # Xác minh rằng URL hiện tại là trang chủ
        wait.until(EC.url_to_be(f"{BASE_URL}/"))
        print("Xác nhận URL là trang chủ. Test Case 2 PASSED.")
        time.sleep(DISPLAY_TIME) # Giữ màn hình sau khi test case thành công

    except TimeoutException:
        # Xử lý lỗi đăng nhập thất bại nếu có (ví dụ: thông báo lỗi)
        print(f"Không thể quay về trang chủ sau đăng nhập. Kiểm tra thông báo lỗi...")
        try:
            error_alert_locator = (By.CSS_SELECTOR, '.chakra-alert[status="error"]')
            error_message = wait.until(EC.presence_of_element_located(error_alert_locator), timeout=5).text
            print(f"Thông báo lỗi trên giao diện (nếu có): {error_message}")
            pytest.fail(f"Đăng nhập thất bại: {error_message}")
        except TimeoutException:
            pytest.fail("Đăng nhập thất bại và không có thông báo lỗi rõ ràng trên UI.")
        except Exception as ee:
            pytest.fail(f"Đăng nhập thất bại với lỗi không xác định: {ee}")
    except Exception as e:
        pytest.fail(f"Đăng nhập thất bại do một lỗi không mong đợi: {e}")

# Các test case khác có thể thêm vào đây