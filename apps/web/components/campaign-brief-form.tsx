'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, Rocket, Plus, X } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import type { BrandProfile, MarketingChannel } from '@/lib/types';
import { MARKETING_CHANNEL_LABELS } from '@/lib/types';

interface CampaignBriefFormProps {
  brandProfile: BrandProfile;
}

const ALL_CHANNELS: MarketingChannel[] = [
  'SOCIAL_MEDIA',
  'EMAIL',
  'PAID_ADS',
  'LANDING_PAGE',
  'BLOG',
  'VIDEO',
  'PRINT',
];

const BUDGET_OPTIONS = [
  { value: '', label: 'Not specified' },
  { value: 'Under $1K', label: 'Under $1,000' },
  { value: '$1K-$5K', label: '$1,000 – $5,000' },
  { value: '$5K-$20K', label: '$5,000 – $20,000' },
  { value: '$20K+', label: '$20,000+' },
];

const TIMELINE_OPTIONS = [
  { value: '', label: 'Not specified' },
  { value: '2', label: '2 weeks' },
  { value: '4', label: '4 weeks' },
  { value: '8', label: '8 weeks' },
  { value: '12', label: '12 weeks' },
];

export function CampaignBriefForm({ brandProfile }: CampaignBriefFormProps) {
  const router = useRouter();

  const [objective, setObjective] = React.useState('');
  const [audienceInput, setAudienceInput] = React.useState('');
  const [audiences, setAudiences] = React.useState<string[]>(brandProfile.target_audience ?? []);
  const [channels, setChannels] = React.useState<MarketingChannel[]>(['SOCIAL_MEDIA', 'EMAIL']);
  const [budget, setBudget] = React.useState('');
  const [timeline, setTimeline] = React.useState('');
  const [constraintsRaw, setConstraintsRaw] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const toggleChannel = (channel: MarketingChannel) => {
    setChannels((prev) =>
      prev.includes(channel) ? prev.filter((c) => c !== channel) : [...prev, channel]
    );
  };

  const addAudience = () => {
    const trimmed = audienceInput.trim();
    if (trimmed && !audiences.includes(trimmed)) {
      setAudiences((prev) => [...prev, trimmed]);
      setAudienceInput('');
    }
  };

  const removeAudience = (a: string) => setAudiences((prev) => prev.filter((x) => x !== a));

  const handleSubmit = async () => {
    if (!objective.trim()) {
      setError('Please enter a campaign objective.');
      return;
    }
    if (channels.length === 0) {
      setError('Please select at least one marketing channel.');
      return;
    }

    setLoading(true);
    setError(null);

    const constraints = constraintsRaw
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean);

    try {
      const campaign = await api.campaigns.run({
        brand_profile: brandProfile,
        objective: objective.trim(),
        target_audience: audiences,
        channels,
        budget_range: budget || undefined,
        timeline_weeks: timeline ? parseInt(timeline, 10) : undefined,
        constraints,
      });
      router.push(`/results/${campaign.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to generate campaign. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Campaign Brief</CardTitle>
        <CardDescription>
          Define your campaign objective and BrandOS will generate a complete strategy.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Objective */}
        <div className="space-y-2">
          <Label htmlFor="objective">
            Campaign Objective <span className="text-destructive">*</span>
          </Label>
          <Textarea
            id="objective"
            placeholder="e.g. Increase brand awareness among Gen Z consumers and drive 20% more sign-ups in Q4"
            className="min-h-[90px]"
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
          />
        </div>

        {/* Target Audience */}
        <div className="space-y-2">
          <Label>Target Audience</Label>
          <div className="flex gap-2">
            <Input
              placeholder="e.g. Remote tech workers, age 25–40"
              value={audienceInput}
              onChange={(e) => setAudienceInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addAudience())}
            />
            <Button type="button" variant="outline" size="icon" onClick={addAudience}>
              <Plus className="w-4 h-4" />
            </Button>
          </div>
          {audiences.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {audiences.map((a) => (
                <Badge key={a} variant="secondary" className="pl-2 pr-1 py-1 flex items-center gap-1">
                  {a}
                  <button
                    onClick={() => removeAudience(a)}
                    className="ml-1 hover:text-destructive transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Marketing Channels */}
        <div className="space-y-2">
          <Label>
            Marketing Channels <span className="text-destructive">*</span>
          </Label>
          <div className="flex flex-wrap gap-2">
            {ALL_CHANNELS.map((ch) => (
              <button
                key={ch}
                type="button"
                onClick={() => toggleChannel(ch)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                  channels.includes(ch)
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'border-border text-muted-foreground hover:border-primary/50 hover:text-foreground'
                }`}
              >
                {MARKETING_CHANNEL_LABELS[ch]}
              </button>
            ))}
          </div>
        </div>

        {/* Budget & Timeline */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="budget">Budget Range</Label>
            <select
              id="budget"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {BUDGET_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="timeline">Timeline</Label>
            <select
              id="timeline"
              value={timeline}
              onChange={(e) => setTimeline(e.target.value)}
              className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {TIMELINE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Constraints */}
        <div className="space-y-2">
          <Label htmlFor="constraints">
            Constraints{' '}
            <span className="text-muted-foreground text-xs">(optional — one per line)</span>
          </Label>
          <Textarea
            id="constraints"
            placeholder={`No competitor mentions\nMust include sustainability angle\nBrand-safe imagery only`}
            className="min-h-[80px] font-mono text-sm"
            value={constraintsRaw}
            onChange={(e) => setConstraintsRaw(e.target.value)}
          />
        </div>

        {/* Error */}
        {error && (
          <p className="text-sm text-destructive bg-destructive/10 rounded-md px-3 py-2">{error}</p>
        )}

        {/* Submit */}
        <Button
          onClick={handleSubmit}
          disabled={loading || !objective.trim() || channels.length === 0}
          className="w-full h-12 text-base font-semibold"
          size="lg"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Generating Complete Campaign…
            </>
          ) : (
            <>
              <Rocket className="mr-2 h-5 w-5" />
              Generate Complete Campaign
            </>
          )}
        </Button>

        {loading && (
          <p className="text-center text-sm text-muted-foreground animate-pulse">
            Generating complete campaign (strategy + assets + quality report)... This takes 60–90 seconds.
          </p>
        )}
      </CardContent>
    </Card>
  );
}