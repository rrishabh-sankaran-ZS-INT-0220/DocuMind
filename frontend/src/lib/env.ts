export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL!,
  backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL!,
  googleLoginUrl: process.env.NEXT_PUBLIC_GOOGLE_LOGIN_URL!,
  googleCallbackUrl: process.env.NEXT_PUBLIC_GOOGLE_CALLBACK_URL!,
  appName: process.env.NEXT_PUBLIC_APP_NAME!,
  appUrl: process.env.NEXT_PUBLIC_APP_URL!,
  enableAnalytics:
    process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === "true",
  enableDebug:
    process.env.NEXT_PUBLIC_ENABLE_DEBUG === "true",
  defaultTheme:
    process.env.NEXT_PUBLIC_DEFAULT_THEME ?? "light",
};