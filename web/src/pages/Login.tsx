import { useT } from "@/i18n"

export default function Login() {
  const t = useT()
  return <h1 className="text-h1">{t("login.title")}</h1>
}
