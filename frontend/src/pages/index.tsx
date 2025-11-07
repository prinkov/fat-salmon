/* eslint-disable prettier/prettier */
import Head from "next/head";
import {
  Badge,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  CardMedia,
  Grid,
  Toolbar,
  Typography,
  useTheme,
} from "@mui/material";
import { products } from "@/products";
import { useReducer } from "react";
import { useRouter } from "next/router";

export default function Home() {
  const theme = useTheme();
  const router = useRouter();

  type Action =
    | { type: "ADD_PRODUCT"; product: any }
    | { type: "REMOVE_PRODUCT"; name: string };

  const updateCart = (cart: any[], action: Action) => {
    switch (action.type) {
      case "ADD_PRODUCT": {
        const existingProduct = cart.find(
          (p: any) => p.name === action.product.name
        );
        if (existingProduct) {
          return cart.map((p: any) =>
            p.name === action.product.name
              ? { ...p, quantity: p.quantity + 1 }
              : p
          );
        } else {
          return [...cart, { ...action.product, quantity: 1 }];
        }
      }
      case "REMOVE_PRODUCT": {
        const index = cart.findIndex((p: any) => p.name === action.name);
        if (index !== -1) {
          const product = cart[index];
          if (product.quantity > 1) {
            return [
              ...cart.slice(0, index),
              { ...product, quantity: product.quantity - 1 },
              ...cart.slice(index + 1),
            ];
          } else {
            return [...cart.slice(0, index), ...cart.slice(index + 1)];
          }
        } else {
          return cart;
        }
      }
      default:
        throw new Error(`Invalid action type ${action}`);
    }
  };

  const [cart, setCart] = useReducer(updateCart, []);

  return (
    <>
      <Head>
        <title>Fat Salmon</title>
        <meta
            name="description"
            content="Fat Salmon — доставка роллов в Тбилиси"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Box p={2} pb={theme.spacing(8)}>
        <Toolbar />
        <Grid
          container
          spacing={2}
          justifyContent="center"
          sx={{
            display: "flex",
            flexWrap: "wrap",
            gap: 1,
          }}>
          {products.map((product) => (
            <Grid item
              key={product.name}
              sx={{
              width: 200
              }}>
              <Badge
                badgeContent={
                  cart.find((p: any) => p.name === product.name)?.quantity
                }
                color="primary"
                sx={{
                  "& .MuiBadge-badge": {
                    color: "white",
                  },
                }}
              >
                <Card
                    sx={{
                      height: 255,
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "space-between",
                    }}
                >
                  <CardMedia
                    component="img"
                    image={product.image}
                    sx={{
                      p: 3,
                      height: 155,
                      objectFit: "cover", // обрезает аккуратно, не растягивая
                      borderBottom: "1px solid #eee",
                      borderRadius: theme.spacing(2),
                    }}
                  />

                  <CardContent
                    sx={{
                            py: 1,
                            flexGrow: 1,
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                            textAlign: "center",
                    }}
                  >
                    <Typography
                      variant="body1"
                      sx={{
                        verticalAlign: "middle",
                        fontWeight: 500,
                      }}
                    >
                      {product.name} — <b>{product.price} ₾</b>
                    </Typography>
                  </CardContent>

                  <CardActions>
                    {cart.find((p: any) => p.name === product.name) ? (
                      <>
                        <Button
                          onClick={() =>
                            setCart({
                              type: "REMOVE_PRODUCT",
                              name: product.name,
                            })
                          }
                          variant="outlined"
                          sx={{
                            height: theme.spacing(4),
                            width: "50%",
                            fontWeight: "bold",
                          }}
                        >
                          −
                        </Button>

                        <Button
                          onClick={() =>
                            setCart({
                              type: "ADD_PRODUCT",
                              product: product,
                            })
                          }
                          variant="outlined"
                          sx={{
                            height: theme.spacing(4),
                            width: "50%",
                            fontWeight: "bold",
                          }}
                        >
                          +
                        </Button>
                      </>
                    ) : (
                      <Button
                        onClick={() =>
                          setCart({
                            type: "ADD_PRODUCT",
                            product: product,
                          })
                        }
                        variant="outlined"
                        sx={{ fontWeight: 600 }}
                      >
                        Добавить
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Badge>
            </Grid>
          ))}
        </Grid>
      </Box>

      {cart.length > 0 && (
        <Button
          variant="contained"
          sx={{
            position: "fixed",
            right: theme.spacing(1),
            left: theme.spacing(1),
            height: theme.spacing(6),
            width: "auto",
            color: "white",
            bottom: theme.spacing(1),
            fontWeight: 600,
          }}
          onClick={() => {
            if (typeof window !== "undefined") {
              localStorage.setItem("cart", JSON.stringify(cart));
              router.push("/checkout");
            }
          }}
        >
          Оплатить — {cart.length} {cart.length > 1 ? "товара" : "товар"} на{" "}
          {Math.round(
            cart.reduce(
              (acc: number, p: any) => acc + p.price * p.quantity,
              0
            ) * 100
          ) / 100}{" "}
          ₾
        </Button>
      )}
    </>
  );
}
