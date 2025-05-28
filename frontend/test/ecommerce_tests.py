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

        # Tùy chọn: Chờ Alert biến mất
        wait.until_not(EC.alert_is_present())
        print("Alert đã biến mất.")

        print("Xác nhận đăng ký thành công qua JavaScript Alert. Test Case 1 PASSED.")
        time.sleep(DISPLAY_TIME) # Giữ màn hình sau khi test case thành công

        # --- Gán thông tin tài khoản để Test Case 2 có thể sử dụng ---
        pytest.register_email = register_email
        pytest.register_password = register_password

    except TimeoutException as e:
        print(f"Lỗi Timeout khi chờ JavaScript Alert: {e}. Có thể không phải là Alert thông thường.")
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
    login_email = "user24@gmail.com"
    login_password = "thanh12345"

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

    # --- BƯỚC CẢI TIẾN: Đảm bảo đăng xuất trước khi tiến hành đăng nhập ---
    print('Kiểm tra trạng thái đăng nhập và thực hiện đăng xuất nếu cần.')
    try:
        profile_link_locator = (By.XPATH, '//a[contains(@href, "/profile")]')
        wait.until(EC.visibility_of_element_located(profile_link_locator), timeout=3)
        profile_link = driver.find_element(*profile_link_locator)
        profile_link.click()
        print("Đã click vào Profile để tiến hành đăng xuất.")

        logout_button_locator = (By.XPATH, '//button[text()="Logout"]')
        logout_button = wait.until(EC.element_to_be_clickable(logout_button_locator), timeout=3)
        logout_button.click()
        print('Đã click nút "Logout".')

        wait.until(EC.url_to_be(f"{BASE_URL}/"), timeout=10)
        print('Đã đăng xuất thành công và quay về trang chủ.')

    except (TimeoutException, NoSuchElementException):
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

    # --- SỬA ĐỔI Ở ĐÂY: CHỜ NÚT PROFILE HOẶC BASKET HIỂN THỊ ĐỂ XÁC NHẬN ĐĂNG NHẬP THÀNH CÔNG ---
    print("Chờ nút 'Profile' hoặc 'Basket' hiển thị để xác nhận đăng nhập thành công.")
    try:
        # Chờ nút 'Profile' hoặc 'Basket' (có chứa số lượng) xuất hiện
        # Nút 'Profile' là một dấu hiệu tốt cho việc đăng nhập thành công
        profile_or_basket_locator = (By.XPATH, '//a[contains(@href, "/profile")] | //button[contains(., "Basket")]')
        wait.until(EC.visibility_of_element_located(profile_or_basket_locator),
                   message="Không tìm thấy nút 'Profile' hoặc 'Basket' sau khi đăng nhập.")
        print("Đã xác nhận đăng nhập thành công (nút Profile/Basket đã hiển thị).")

        # Sau khi đăng nhập, URL có thể vẫn ở /signin hoặc chuyển sang /profile
        # Nếu muốn chắc chắn quay về trang chủ, có thể thêm driver.get(BASE_URL) ở đây,
        # nhưng việc chờ element hiển thị là đủ xác nhận đăng nhập thành công.
        # driver.get(BASE_URL) # Bỏ comment nếu muốn cứng nhắc quay về trang chủ

        print("Test Case 2 PASSED: Đăng nhập thành công và xác nhận trên UI.")
        time.sleep(DISPLAY_TIME)

    except TimeoutException:
        print(f"Không xác nhận được đăng nhập thành công (nút Profile/Basket không hiển thị). Kiểm tra thông báo lỗi...")
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

# Test Case 3: Thêm sản phẩm vào giỏ hàng và sau đó click vào button Basket
def test_03_add_product_to_basket_and_view_basket(driver):
    print("\n--- Test Case 3: Thêm sản phẩm vào giỏ hàng và kiểm tra giỏ hàng ---")
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # Bước 1: Đăng nhập (sử dụng logic từ Test Case 2 để đảm bảo đã đăng nhập)
    print("Thực hiện đăng nhập để chuẩn bị cho việc thêm sản phẩm vào giỏ hàng.")
    login_email = "user24@gmail.com"
    login_password = "thanh12345"

    try:
        if hasattr(pytest, 'register_email') and hasattr(pytest, 'register_password'):
            login_email = pytest.register_email
            login_password = pytest.register_password
            print("Sử dụng tài khoản từ test đăng ký trước đó để đăng nhập.")
        else:
            print(f"Không tìm thấy tài khoản từ test đăng ký. Sử dụng tài khoản mặc định: {login_email}")
    except AttributeError:
        print(f"Không tìm thấy tài khoản từ test đăng ký. Sử dụng tài khoản mặc định: {login_email}")

    driver.get(BASE_URL) # Đảm bảo ở trang chủ trước khi kiểm tra trạng thái đăng nhập

    # Thực hiện đăng xuất nếu đã đăng nhập (logic tương tự TC2)
    print('Kiểm tra trạng thái đăng nhập và thực hiện đăng xuất nếu cần trước khi đăng nhập lại cho TC3.')
    try:
        profile_link_locator = (By.XPATH, '//a[contains(@href, "/profile")]')
        wait.until(EC.visibility_of_element_located(profile_link_locator), timeout=3)
        profile_link = driver.find_element(*profile_link_locator)
        profile_link.click()
        print("Đã click vào Profile để kiểm tra trạng thái đăng nhập.")

        logout_button_locator = (By.XPATH, '//button[text()="Logout"]')
        logout_button = wait.until(EC.element_to_be_clickable(logout_button_locator), timeout=3)
        logout_button.click()
        print('Đã click nút "Logout".')
        wait.until(EC.url_to_be(f"{BASE_URL}/"), timeout=5)
        print('Đã đăng xuất thành công.')
    except (TimeoutException, NoSuchElementException):
        print('Chưa đăng nhập hoặc không tìm thấy nút Profile/Logout. Tiếp tục.')
    except Exception as e:
        print(f"Lỗi không xác định khi cố gắng đăng xuất trong TC3: {e}. Tiếp tục.")

    # Tiến hành đăng nhập
    try:
        login_nav_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="/signin"]/button[text()="Login"]'))
        )
        login_nav_button.click()
        wait.until(EC.url_contains("/signin"))
        wait.until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(login_email)
        driver.find_element(By.NAME, "password").send_keys(login_password)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        print(f"Đã điền thông tin và click đăng nhập với email: {login_email} cho Test Case 3.")

        # --- SỬA ĐỔI Ở ĐÂY: CHỜ NÚT PROFILE HOẶC BASKET HIỂN THỊ ĐỂ XÁC NHẬN ĐĂNG NHẬP THÀNH CÔNG ---
        print("Chờ nút 'Profile' hoặc 'Basket' hiển thị để xác nhận đăng nhập thành công cho TC3.")
        profile_or_basket_locator = (By.XPATH, '//a[contains(@href, "/profile")] | //button[contains(., "Basket")]')
        wait.until(EC.visibility_of_element_located(profile_or_basket_locator),
                   message="Không tìm thấy nút 'Profile' hoặc 'Basket' sau khi đăng nhập trong TC3.")
        print("Đã xác nhận đăng nhập thành công cho Test Case 3.")

        # Điều hướng về trang chủ sau khi xác nhận đăng nhập thành công
        driver.get(BASE_URL)
        wait.until(EC.url_to_be(f"{BASE_URL}/"))
        print("Đã quay về trang chủ sau khi đăng nhập và xác nhận.")

    except TimeoutException:
        pytest.fail("Đăng nhập thất bại cho Test Case 3 hoặc không xác nhận được trạng thái đăng nhập.")
    except Exception as e:
        pytest.fail(f"Lỗi không mong đợi trong quá trình đăng nhập cho TC3: {e}")

    # Bước 2: Tìm và click "Add to Basket" của sản phẩm đầu tiên
    print("Tìm và click 'Add to Basket' cho sản phẩm đầu tiên.")
    try:
        # Tìm nút "Add to Basket" đầu tiên
        add_to_basket_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '(//button[text()="Add to Basket"])[1]'))
        )
        add_to_basket_button.click()
        print("Đã click 'Add to Basket' cho sản phẩm đầu tiên.")
    except TimeoutException:
        pytest.fail("Không tìm thấy nút 'Add to Basket' cho sản phẩm đầu tiên.")
    except Exception as e:
        pytest.fail(f"Lỗi khi click 'Add to Basket': {e}")

    # Bước 3: Xác minh cập nhật giỏ hàng (Basket (1))
    print("Xác minh số lượng sản phẩm trong giỏ hàng.")
    try:
        basket_counter_locator = (By.XPATH, '//button[contains(., "Basket")]') # Tìm button có text "Basket"
        # Chờ cho văn bản của nút Basket hiển thị "Basket (1)" hoặc tương tự
        wait.until(EC.text_to_be_present_in_element(basket_counter_locator, "Basket (1)"),
                   message="Số lượng giỏ hàng không cập nhật thành (1).")
        print("Số lượng sản phẩm trong giỏ hàng đã cập nhật thành 'Basket (1)'.")
    except TimeoutException:
        pytest.fail("Số lượng giỏ hàng không hiển thị đúng sau khi thêm sản phẩm.")
    except Exception as e:
        pytest.fail(f"Lỗi khi xác minh giỏ hàng: {e}")

    # Bước 4: Click vào nút "Basket" nằm bên cạnh "Profile"
    print("Click vào nút 'Basket' để xem giỏ hàng.")
    try:
        basket_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Basket")]')) # Lại sử dụng locator này
        )
        basket_button.click()
        print("Đã click nút 'Basket'.")
    except TimeoutException:
        pytest.fail("Không tìm thấy hoặc không click được nút 'Basket' trên Navbar.")
    except Exception as e:
        pytest.fail(f"Lỗi khi click nút Basket: {e}")

    # Bước 5: Xác minh sản phẩm đã thêm hiển thị trên trang giỏ hàng
    print("Xác minh sản phẩm trong trang giỏ hàng.")
    try:
        # Chờ URL chuyển đến trang giỏ hàng (có thể là /basket hoặc /cart)
        # Dựa trên file structure image_9ba1f9.png, có thư mục "Basket" trong "pages", nên /basket là hợp lý.
        wait.until(EC.url_contains("/basket") or EC.url_contains("/cart"))
        print("Đã chuyển đến trang giỏ hàng.")

        # Xác minh tên sản phẩm (giả định tên sản phẩm là "iPhone 16 Pro Max 123" từ hình ảnh)
        product_name_in_basket_locator = (By.XPATH, '//p[text()="iPhone 16 Pro Max 123"]')
        wait.until(EC.presence_of_element_located(product_name_in_basket_locator),
                   message="Không tìm thấy sản phẩm 'iPhone 16 Pro Max 123' trong giỏ hàng.")
        print("Sản phẩm 'iPhone 16 Pro Max 123' đã hiển thị trong giỏ hàng.")

        print("Test Case 3 PASSED: Thêm sản phẩm vào giỏ hàng và kiểm tra thành công.")
        time.sleep(DISPLAY_TIME) # Giữ màn hình sau khi test case thành công

    except TimeoutException:
        pytest.fail("Không chuyển đến trang giỏ hàng hoặc sản phẩm không hiển thị trong giỏ.")
    except Exception as e:
        pytest.fail(f"Lỗi khi xác minh sản phẩm trong giỏ hàng: {e}")