import type { CampaignStrategy } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Target, MessageSquare, BarChart2, Lightbulb, Clock, TrendingUp } from 'lucide-react';

interface CampaignStrategyCardProps {
  strategy: CampaignStrategy;
}

export function CampaignStrategyCard({ strategy }: CampaignStrategyCardProps) {
  return (
    <div className="space-y-6">
      {/* Campaign Header */}
      <Card className="border-primary/30 bg-primary/5">
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-primary mb-1">Campaign Name</p>
              <h2 className="text-2xl font-bold">{strategy.campaign_name}</h2>
            </div>
            <Badge variant="outline" className="shrink-0 border-primary/40 text-primary">
              <Clock className="w-3 h-3 mr-1" />
              {strategy.content_calendar_weeks} weeks
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-1">Positioning Statement</p>
          <p className="text-base italic text-foreground/90 leading-relaxed">
            &ldquo;{strategy.positioning_statement}&rdquo;
          </p>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Messaging Pillars */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-blue-400" />
              Messaging Pillars
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="space-y-3">
              {strategy.messaging_pillars.map((pillar, i) => (
                <li key={i} className="flex gap-3 items-start">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 text-xs flex items-center justify-center font-bold mt-0.5">
                    {i + 1}
                  </span>
                  <p className="text-sm text-foreground/85 leading-relaxed">{pillar}</p>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>

        {/* Key Themes */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-yellow-400" />
              Key Themes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {strategy.key_themes.map((theme, i) => (
                <Badge
                  key={i}
                  variant="secondary"
                  className="text-sm py-1 px-3"
                >
                  {theme}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Channel Strategy */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Target className="w-4 h-4 text-purple-400" />
            Channel Strategy
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-border">
            {Object.entries(strategy.channel_strategy).map(([channel, approach]) => (
              <div key={channel} className="py-3 first:pt-0 last:pb-0">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                  {channel.replace(/_/g, ' ')}
                </p>
                <p className="text-sm text-foreground/85">{approach}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Success Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-green-400" />
              Success Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {strategy.success_metrics.map((metric, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-foreground/85">
                  <span className="text-green-400 mt-0.5">✓</span>
                  {metric}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Rationale */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-orange-400" />
              Strategic Rationale
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-foreground/85 leading-relaxed">{strategy.rationale}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
