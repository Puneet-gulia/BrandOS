import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { BrandProfile } from "@/lib/types"

interface BrandProfileCardProps {
  profile: BrandProfile
}

export function BrandProfileCard({ profile }: BrandProfileCardProps) {
  return (
    <Card className="w-full max-w-4xl mx-auto border-border bg-card/50 backdrop-blur">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-3xl mb-2">{profile.company_name}</CardTitle>
            {profile.tagline && <CardDescription className="text-lg">{profile.tagline}</CardDescription>}
          </div>
          <Badge variant="secondary" className="text-sm px-3 py-1">{profile.industry}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2 text-sm text-muted-foreground uppercase tracking-wider">Brand Voice & Tone</h4>
              <div className="flex flex-wrap gap-2">
                <Badge variant="default" className="bg-primary/20 text-primary hover:bg-primary/30 border-0">{profile.tone}</Badge>
                {profile.brand_voice.map((voice, i) => (
                  <Badge key={i} variant="outline">{voice}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-2 text-sm text-muted-foreground uppercase tracking-wider">Target Audience</h4>
              <ul className="list-disc list-inside text-sm space-y-1">
                {profile.target_audience.map((aud, i) => (
                  <li key={i}>{aud}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2 text-sm text-muted-foreground uppercase tracking-wider">Keywords</h4>
              <div className="flex flex-wrap gap-2">
                {profile.keywords.map((kw, i) => (
                  <Badge key={i} variant="secondary" className="text-xs">{kw}</Badge>
                ))}
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="bg-secondary/30 p-4 rounded-lg border border-secondary">
              <h4 className="font-semibold mb-2 text-sm text-muted-foreground uppercase tracking-wider">Unique Selling Proposition</h4>
              <p className="text-sm">{profile.unique_selling_proposition}</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2 text-sm text-muted-foreground uppercase tracking-wider">Core Values</h4>
              <ul className="list-disc list-inside text-sm space-y-1">
                {profile.core_values.map((val, i) => (
                  <li key={i}>{val}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}\n