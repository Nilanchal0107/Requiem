import { useT } from "@/i18n"
import Hero from "@/pages/home/Hero"
import Problem from "@/pages/home/Problem"
import HowItWorks from "@/pages/home/HowItWorks"
import Different from "@/pages/home/Different"
import Features from "@/pages/home/Features"
import Schemes from "@/pages/home/Schemes"
import Team from "@/pages/home/Team"

export default function Home() {
  const t = useT()
  return (
    <>
      <h1 className="text-h1">{t("home.title")}</h1>
      <Hero />
      <Problem />
      <HowItWorks />
      <Different />
      <Features />
      <Schemes />
      <Team />
    </>
  )
}
