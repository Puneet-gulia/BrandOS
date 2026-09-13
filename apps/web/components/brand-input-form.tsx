"use client"

import * as React from "react"
import { Globe, FileText, Upload, Loader2, CheckCircle2 } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { api } from "@/lib/api"
import type { BrandProfile } from "@/lib/types"

interface BrandInputFormProps {
  onSuccess: (profile: BrandProfile) => void
}

export function BrandInputForm({ onSuccess }: BrandInputFormProps) {
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  
  const [url, setUrl] = React.useState("")
  const [text, setText] = React.useState("")
  const [file, setFile] = React.useState<File | null>(null)

  const handleExtractUrl = async () => {
    setLoading(true)
    setError(null)
    try {
      const profile = await api.knowledge.extract({ input_type: 'url', url })
      onSuccess(profile)
    } catch (err: any) {
      setError(err.message || 'Failed to extract from URL')
    } finally {
      setLoading(false)
    }
  }

  const handleExtractText = async () => {
    setLoading(true)
    setError(null)
    try {
      const profile = await api.knowledge.extract({ input_type: 'text', text })
      onSuccess(profile)
    } catch (err: any) {
      setError(err.message || 'Failed to extract from text')
    } finally {
      setLoading(false)
    }
  }

  const handleExtractFile = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const profile = await api.knowledge.extractFile(file)
      onSuccess(profile)
    } catch (err: any) {
      setError(err.message || 'Failed to extract from file')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-2xl mx-auto border-border">
      <CardHeader>
        <CardTitle className="text-2xl">Brand Knowledge Extraction</CardTitle>
        <CardDescription>
          Provide your brand context. We will analyze it and generate a complete brand profile.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="url" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="url"><Globe className="w-4 h-4 mr-2" />Website URL</TabsTrigger>
            <TabsTrigger value="text"><FileText className="w-4 h-4 mr-2" />Text Description</TabsTrigger>
            <TabsTrigger value="document"><Upload className="w-4 h-4 mr-2" />Upload Document</TabsTrigger>
          </TabsList>
          
          <TabsContent value="url" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="url">Company Website</Label>
              <Input
                id="url"
                placeholder="https://yourcompany.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
            </div>
            {error && <p className="text-destructive text-sm">{error}</p>}
            <Button onClick={handleExtractUrl} disabled={loading || !url} className="w-full">
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? "Analyzing Brand..." : "Analyze Brand"}
            </Button>
          </TabsContent>

          <TabsContent value="text" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="text">Brand Description</Label>
              <Textarea
                id="text"
                placeholder="Describe your company, products, tone of voice, and target audience..."
                className="min-h-[150px]"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </div>
            {error && <p className="text-destructive text-sm">{error}</p>}
            <Button onClick={handleExtractText} disabled={loading || text.length < 10} className="w-full">
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? "Analyzing Brand..." : "Analyze Brand"}
            </Button>
          </TabsContent>

          <TabsContent value="document" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="file">Upload Brand Guidelines (.txt, .pdf)</Label>
              <Input
                id="file"
                type="file"
                accept=".txt,.pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </div>
            {error && <p className="text-destructive text-sm">{error}</p>}
            <Button onClick={handleExtractFile} disabled={loading || !file} className="w-full">
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? "Analyzing Brand..." : "Analyze Brand"}
            </Button>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}\n