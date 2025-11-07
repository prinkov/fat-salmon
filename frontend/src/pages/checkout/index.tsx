/* eslint-disable prettier/prettier */
import {
  Box,
  Button,
  IconButton,
  Toolbar,
  Typography,
  useTheme,
} from "@mui/material";
import Head from "next/head";
import { useEffect, useState } from "react";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import Image from "next/image";
import { useRouter } from "next/router";
import { useTonConnectUI, useTonWallet } from "@tonconnect/ui-react";
import { useSender } from "@tonpay/react";
import { Currencies, Tonpay } from "@tonpay/sdk";

export default function CheckoutPage() {
  const [tonConnectUI] = useTonConnectUI();
  const theme = useTheme();
  const router = useRouter();
  const { sender } = useSender(tonConnectUI);
  const wallet = useTonWallet();
  const [tonpay, setTonpay] = useState<Tonpay>();
  const [cart, setCart] = useState<any[]>([]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    setCart(JSON.parse(localStorage.getItem("cart") || "[]"));
  }, []);

  useEffect(() => {
    if (!sender || tonpay) return;
    Tonpay.create("testnet", sender).then((instance) => setTonpay(instance));
  }, [sender]);

  const total = Math.round(
    cart.reduce((acc, p) => acc + p.price * p.quantity, 0) * 100
  ) / 100;

  return (
    <>
      <Head>
        <title>Fat Salmon — Оплата</title>
      </Head>

      <Box p={2} pb={theme.spacing(10)} sx={{ maxWidth: 600, mx: "auto" }}>
        <Toolbar />

        <Box display="flex" alignItems="center" mb={3}>
          <IconButton onClick={() => router.back()} sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h5" fontWeight={700}>
            Оформление заказа
          </Typography>
        </Box>

        {cart.length === 0 ? (
          <Typography variant="body1" textAlign="center" mt={8}>
            Корзина пуста 😔
          </Typography>
        ) : (
          cart.map((product) => (
            <Box
              key={product.name}
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                mb: 2,
                p: 2,
                borderRadius: 3,
                backgroundColor: "#fff",
                boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center" }} gap={2}>
                <Image
                  src={`/${product.image}`}
                  width={72}
                  height={72}
                  alt={product.name}
                  style={{ borderRadius: "8px", objectFit: "cover" }}
                />
                <Box>
                  <Typography fontWeight={600}>{product.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {product.quantity} шт.
                  </Typography>
                </Box>
              </Box>

              <Typography fontWeight={600}>
                {product.price * product.quantity} ₾
              </Typography>
            </Box>
          ))
        )}

        {cart.length > 0 && (
          <>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mt: 4,
                mb: 2,
              }}
            >
              <Typography variant="h6" fontWeight={700}>
                Итого
              </Typography>
              <Typography variant="h6" fontWeight={700}>
                {total} ₾
              </Typography>
            </Box>

            <Button
              variant="contained"
              disabled={!sender || !tonpay || !wallet}
              sx={{
                position: "fixed",
                bottom: theme.spacing(1.5),
                left: theme.spacing(1.5),
                right: theme.spacing(1.5),
                height: theme.spacing(6),
                backgroundColor: "#E76F51",
                fontWeight: 700,
                color: "#fff",
                borderRadius: 2,
                "&:hover": { backgroundColor: "#d45e44" },
              }}
              onClick={async () => {
                const initData = window.Telegram?.WebApp?.initDataUnsafe;
                const chatId = initData?.user?.id; //
                if (!sender || !tonpay || !wallet) return;
                const invoiceId = Date.now().toString();

                const store = tonpay.getStore(
                  "UQC46A1mTIslictugxIUtibVUKEPgZikdqDiAPfmASDnrIlI"
                );

                const invoice = await store.requestPurchase({
                  invoiceId,
                  amount: total,
                  metadata: JSON.stringify({ chat_id: chatId }),
                  currency: Currencies.TON,
                });

                // Можно отправить webhook в backend для логирования
                await fetch("/tonpay/webhook", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    invoiceId,
                    amount: total,
                    status: "PENDING",
                  }),
                });

                window.location.href = `https://beta.pay.thetonpay.app/i/${invoice.address}`;
              }}
            >
              Оплатить {total} ₾
            </Button>
          </>
        )}
      </Box>
    </>
  );
}
