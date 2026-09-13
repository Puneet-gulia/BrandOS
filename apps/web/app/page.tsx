"use client"

import * as React from "react"
import { BrandInputForm } from "@/components/brand-input-form"
import { BrandProfileCard } from "@/components/brand-profile-card"
import { CampaignBriefForm } from "@/components/campaign-brief-form"
import type { BrandProfile } from "@/lib/types"

export default function Home() {
  const [profile, setProfile] = React.useState<BrandProfile | null>(null)

  return (
    <div className="container mx-auto py-12 px-4 space-y-12">
      <section className="text-center space-y-6 max-w-3xl mx-auto">
        <h2 className="text-5xl font-extrabold tracking-tight sm:text-6xl text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
          Turn your brand into a complete marketing campaign in minutes.
        </h2>
        <p className="text-xl text-muted-foreground">
          BrandOS analyzes your business and automatically generates high-converting strategies, copy, and assets.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <span className="px-4 py-1.5 rounded-full bg-secondary text-secondary-foreground text-sm font-medium">Brand Analysis</span>
          <span className="px-4 py-1.5 rounded-full bg-secondary text-secondary-foreground text-sm font-medium">Campaign Strategy</span>
          <span className="px-4 py-1.5 rounded-full bg-secondary text-secondary-foreground text-sm font-medium">Creative Assets</span>
        </div>
      </section>

      {!profile ? (
        <BrandInputForm onSuccess={setProfile} />
      ) : (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
          <BrandProfileCard profile={profile} />
          <CampaignBriefForm brandProfile={profile} />
        </div>
      )}
    </div>
  )
}\n