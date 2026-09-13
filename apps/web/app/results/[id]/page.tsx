'use client';

import * as React from 'react';
import Link from 'next/link';
import { ArrowLeft, Loader2, AlertCircle, CheckCircle2, Sparkles, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CampaignStrategyCard } from '@/components/campaign-strategy-card';
import { BrandProfileCard } from '@/components/brand-profile-card';
import { CreativeAssetsPanel } from '@/components/creative-assets-panel';
import { QualityReportCard } from '@/components/quality-report-card';
import { api } from '@/lib/api';
import type { CampaignPackage } from '@/lib/types';

interface ResultsPageProps {
  params: { id: string };
}

export default function ResultsPage({ params }: ResultsPageProps) {
  const [campaign, setCampaign] = React.useState<CampaignPackage | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [generatingAssets, setGeneratingAssets] = React.useState(false);
  const [assetsError, setAssetsError] = React.useState<string | null>(null);
  const [evaluating, setEvaluating] = React.useState(false);
  const [evalError, setEvalError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchCampaign = async () => {
      try {
        const data = await api.campaigns.get(params.id);
        setCampaign(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Campaign not found.');
      } finally {
        setLoading(false);
      }
    };

    fetchCampaign();
  }, [params.id]);

  const handleEvaluate = async () => {
    if (!campaign) return;
    setEvaluating(true);
    setEvalError(null);
    try {
      const updated = await api.campaigns.evaluate(campaign.id);
      setCampaign(updated);
    } catch (err) {
      setEvalError(err instanceof Error ? err.message : 'Evaluation failed.');
    } finally {
      setEvaluating(false);
    }
  };

  const handleGenerateAssets = async () => {
    if (!campaign) return;
    setGeneratingAssets(true);
    setAssetsError(null);
    try {
      const updatedCampaign = await api.campaigns.generateAssets(campaign.id);
      setCampaign(updatedCampaign);
    } catch (err: unknown) {
      setAssetsError(err instanceof Error ? err.message : 'Failed to generate assets.');
    } finally {
      setGeneratingAssets(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-20 flex flex-col items-center gap-4">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
        <p className="text-muted-foreground">Loading campaign…</p>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="container mx-auto py-20 max-w-lg text-center space-y-4">
        <AlertCircle className="w-12 h-12 text-destructive mx-auto" />
        <h2 className="text-xl font-semibold">Campaign Not Found</h2>
        <p className="text-muted-foreground">{error ?? 'This campaign does not exist.'}</p>
        <Button asChild>
          <Link href="/">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
        </Button>
      </div>
    );
  }

  const statusConfig = {
    complete: { label: 'Complete', icon: <CheckCircle2 className="w-4 h-4" />, variant: 'default' as const },
    in_progress: { label: 'In Progress', icon: <Loader2 className="w-4 h-4 animate-spin" />, variant: 'secondary' as const },
    failed: { label: 'Failed', icon: <AlertCircle className="w-4 h-4" />, variant: 'destructive' as const },
    draft: { label: 'Draft', icon: null, variant: 'outline' as const },
  };

  const status = statusConfig[campaign.status] ?? statusConfig.draft;

  return (
    <div className="container mx-auto py-10 px-4 space-y-10 max-w-5xl">
      {/* Page Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <Button variant="ghost" size="sm" asChild className="mb-3 -ml-2">
            <Link href="/">
              <ArrowLeft className="w-4 h-4 mr-1" />
              New Campaign
            </Link>
          </Button>
          <h1 className="text-3xl font-bold">
            {campaign.campaign_strategy?.campaign_name ?? 'Campaign Results'}
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Campaign ID: <code className="font-mono text-xs">{campaign.id}</code>
          </p>
        </div>
        <Badge variant={status.variant} className="flex items-center gap-1.5 px-3 py-1.5 text-sm">
          {status.icon}
          {status.label}
        </Badge>
      </div>

      {/* Campaign Summary */}
      <section>
        <Card className="bg-muted/30">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Campaign Name</p>
                <p className="font-semibold line-clamp-2" title={campaign.campaign_strategy?.campaign_name}>{campaign.campaign_strategy?.campaign_name ?? 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Brand</p>
                <p className="font-semibold truncate">{campaign.brand_profile.company_name}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Quality Score</p>
                {campaign.quality_report ? (
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{Math.round(campaign.quality_report.overall_score * 100)}/100</span>
                    <Badge variant={campaign.quality_report.passed ? "default" : "destructive"} className="text-[10px] px-1.5 py-0 h-5">
                      {campaign.quality_report.passed ? 'PASS' : 'FAIL'}
                    </Badge>
                  </div>
                ) : (
                  <p className="font-semibold text-muted-foreground">N/A</p>
                )}
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Assets Generated</p>
                {campaign.campaign_assets ? (
                  <div className="flex flex-wrap gap-1">
                    {campaign.campaign_assets.social_media_posts?.length > 0 && <Badge variant="secondary" className="text-[10px]">{campaign.campaign_assets.social_media_posts.length} Social</Badge>}
                    {campaign.campaign_assets.ad_copy?.length > 0 && <Badge variant="secondary" className="text-[10px]">{campaign.campaign_assets.ad_copy.length} Ads</Badge>}
                    {campaign.campaign_assets.email_campaigns?.length > 0 && <Badge variant="secondary" className="text-[10px]">{campaign.campaign_assets.email_campaigns.length} Emails</Badge>}
                    {campaign.campaign_assets.landing_page_copy && <Badge variant="secondary" className="text-[10px]">1 Landing Page</Badge>}
                  </div>
                ) : (
                  <p className="font-semibold text-muted-foreground">None</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Strategy */}
      {campaign.campaign_strategy ? (
        <section>
          <h2 className="text-lg font-semibold mb-4 text-muted-foreground uppercase tracking-wide text-sm">
            Campaign Strategy
          </h2>
          <CampaignStrategyCard strategy={campaign.campaign_strategy} />
        </section>
      ) : campaign.status === 'failed' ? (
        <Card className="border-destructive/40 bg-destructive/5">
          <CardContent className="py-8 text-center">
            <AlertCircle className="w-10 h-10 text-destructive mx-auto mb-3" />
            <p className="font-semibold">Strategy generation failed.</p>
            <p className="text-sm text-muted-foreground mt-1">
              Please go back and try again with a different brief or brand input.
            </p>
          </CardContent>
        </Card>
      ) : null}

      {/* Creative Assets */}
      {campaign.campaign_strategy && (
        <section>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-muted-foreground uppercase tracking-wide text-sm">
              Creative Assets
            </h2>
          </div>
          
          {campaign.campaign_assets ? (
            <CreativeAssetsPanel assets={campaign.campaign_assets} />
          ) : (
            <Card className="border-dashed border-primary/30 bg-primary/5">
              <CardContent className="py-12 flex flex-col items-center justify-center text-center">
                <Sparkles className="w-12 h-12 text-primary mb-4" />
                <h3 className="text-xl font-semibold mb-2">Generate Creative Assets</h3>
                <p className="text-muted-foreground max-w-md mb-6">
                  Based on the campaign strategy, BrandOS will now generate social media posts, ad copy, emails, landing pages, and image prompts.
                </p>
                
                {assetsError && (
                  <div className="mb-6 p-3 bg-destructive/10 text-destructive text-sm rounded-md flex items-center gap-2 max-w-md">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{assetsError}</span>
                  </div>
                )}
                
                <Button 
                  size="lg" 
                  onClick={handleGenerateAssets}
                  disabled={generatingAssets}
                >
                  {generatingAssets ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Generating creative assets...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      Generate Assets
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          )}
        </section>
      )}

      {campaign.campaign_assets && !campaign.quality_report && (
        <section>
          <h2 className="text-lg font-semibold text-muted-foreground uppercase tracking-wide text-sm mb-4">Quality Evaluation</h2>
          <Card className="border-dashed border-primary/30 bg-primary/5">
            <CardContent className="py-12 flex flex-col items-center justify-center text-center">
              <ShieldCheck className="w-12 h-12 text-primary mb-4" />
              <h3 className="text-xl font-semibold mb-2">Quality Evaluation</h3>
              <p className="text-muted-foreground max-w-md mb-6">Get an AI quality assessment of your generated campaign assets against your brand guidelines.</p>
              
              {evalError && (
                <div className="mb-6 p-3 bg-destructive/10 text-destructive text-sm rounded-md flex items-center gap-2 max-w-md">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{evalError}</span>
                </div>
              )}
              
              <Button onClick={handleEvaluate} disabled={evaluating} size="lg">
                {evaluating ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Evaluating...
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-5 h-5 mr-2" />
                    Evaluate Quality
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </section>
      )}

      {campaign.quality_report && (
        <section>
          <h2 className="text-lg font-semibold text-muted-foreground uppercase tracking-wide text-sm mb-4">Quality Report</h2>
          <QualityReportCard report={campaign.quality_report} />
        </section>
      )}

      {/* Brand Profile (collapsible summary) */}
      <details className="group mt-12 border-t pt-8">
        <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2 list-none font-medium">
          <span className="group-open:rotate-90 transition-transform inline-block">▶</span>
          View Brand Profile
        </summary>
        <div className="mt-4">
          <BrandProfileCard profile={campaign.brand_profile} />
        </div>
      </details>
    </div>
  );
}