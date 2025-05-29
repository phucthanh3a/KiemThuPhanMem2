import * as yup from "yup";

const editScheme = yup.object().shape({
  title: yup.string().min(3, "Title must be at least 3 characters").required("Title is required"),
  description: yup.string().min(5, "Description must be at least 5 characters").required("Description is required"),
  price: yup
    .number()
    .required("Price is required")
    .positive("Price must be a positive number")
    .typeError("Price must be a valid number"),
  photos: yup.array()
    .min(1, "At least one photo is required")
    .of(yup.string().url("Each photo URL must be valid"))
    .required("Photos are required"),
});

export default editScheme;
