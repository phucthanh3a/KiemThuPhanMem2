import React from "react";
import {
  Card,
  Text,
  Image,
  Stack,
  Heading,
  CardBody,
  CardFooter,
  Divider,
  ButtonGroup,
  Button,
} from "@chakra-ui/react";
import { Link } from "react-router-dom";
import moment from "moment";
import { useBasket } from "../../contexts/BasketContext";

function Cards({ item }) {
  const { addToBasket, items } = useBasket();

  const findBasketItem = items.find(
    (basket_item) => basket_item._id === item._id
  );

  return (
    <Card maxW="sm">
      <Link to={`/product/${item._id}`}>
        <CardBody>
          <Image
            src={item.photos[0]}
            alt="Product"
            borderRadius="lg"
            loading="lazy"
            boxSize={300}
            objectFit="cover"
          />
          <Stack mt="6" spacing="3">
            <Heading size="md">{item.title}</Heading>
            <Text>{moment(item.createdAt).format("DD/MM/YYYY")}</Text>
            <Text color="blue.600" fontSize="2xl">
              {item.price}$
            </Text>
          </Stack>
        </CardBody>
        <Divider />
      </Link>
      <CardFooter>
        <ButtonGroup spacing="2">
          {/* NÚT "Add to Cart" này giờ sẽ có logic */}
          <Button
            variant="solid" // Đổi từ 'ghost' sang 'solid' hoặc giữ nguyên tùy ý
            colorScheme={findBasketItem ? "red" : "blue"} // Đổi màu dựa trên trạng thái
            onClick={() => addToBasket(item)} // Gọi hàm addToBasket
          >
            {findBasketItem ? "Remove from Cart" : "Add to Cart"} {/* Đổi chữ */}
          </Button>

          {/* Nút cũ "Add to Basket" có thể bị xóa hoặc thay đổi nếu muốn */}
          {/* Nếu bạn vẫn muốn có 2 nút, nút này có thể là "View Details" hoặc "Quick Buy" */}
          {/* Ví dụ:
          <Button variant="ghost" colorScheme="gray">
            View Details
          </Button>
          */}
        </ButtonGroup>
      </CardFooter>
    </Card>
  );
}

export default Cards;     