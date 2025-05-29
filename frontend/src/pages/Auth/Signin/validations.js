import * as yup from "yup";

const validations = yup.object().shape({
  email: yup.string().email("Email không hợp lệ").required("Email là bắt buộc"),
  password: yup
    .string()
    .min(8, "Mật khẩu phải có ít nhất 8 ký tự.") // sửa min=8 cho phù hợp thông báo
    .required("Mật khẩu là bắt buộc"),
  passwordConfirm: yup
    .string()
    .oneOf([yup.ref("password")], "Mật khẩu xác nhận không khớp")
    .required("Xác nhận mật khẩu là bắt buộc"),
});

export default validations;
