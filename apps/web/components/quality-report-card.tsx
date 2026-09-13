'use client';

import * as React from 'react';
import { ShieldCheck, CheckCircle2, XCircle, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { QualityReport, QualityScore, DIMENSION_LABELS } from '@/lib/types';

interface QualityReportCardProps {
  report: QualityReport;
}

export function QualityReportCard({ report }: QualityReportCardProps) {
  const scorePercent = Math.round(report.overall_score * 100);
  const passedCount = report.scores.filter(s => s.passed).length;
  
  // Score color logic
  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-500';
    if (score >= 0.5) return 'text-amber-500';
    return 'text-red-500';
  };
  
  const getStrokeColor = (score: number) => {
    if (score >= 0.7) return 'stroke-green-500';
    if (score >= 0.5) return 'stroke-amber-500';
    return 'stroke-red-500';
  };

  return (
    <div className="space-y-6">
      {/* Overall Score Banner */}
      <Card className={`border-2 ${report.passed ? 'border-green-500/20 bg-green-500/5' : 'border-red-500/20 bg-red-500/5'}`}>
        <CardContent className="p-6 flex items-center justify-between gap-6 flex-wrap">
          <div className="flex items-center gap-6">
            <div className="relative w-24 h-24 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle className="stroke-muted fill-none" cx="50" cy="50" r="40" strokeWidth="8" />
                <circle 
                  className={`fill-none ${getStrokeColor(report.overall_score)} transition-all duration-1000 ease-in-out`}
                  cx="50" cy="50" r="40" strokeWidth="8"
                  strokeDasharray={`${report.overall_score * 251.2} 251.2`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute flex flex-col items-center justify-center text-center">
                <span className={`text-2xl font-bold ${getScoreColor(report.overall_score)}`}>{scorePercent}%</span>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <h3 className="text-xl font-bold">Overall Quality Score</h3>
                <Badge variant={report.passed ? 'default' : 'destructive'} className={report.passed ? 'bg-green-500' : ''}>
                  {report.passed ? 'Passed' : 'Failed'}
                </Badge>
              </div>
              <p className="text-muted-foreground">
                {passedCount} / {report.scores.length} dimensions passed
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Per-Dimension Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {report.scores.map((score) => (
          <DimensionCard key={score.dimension} score={score} />
        ))}
      </div>

      {/* Recommendations */}
      {report.recommendations && report.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-amber-500" />
              AI Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {report.recommendations.map((rec, i) => (
                <li key={i} className="flex gap-3 text-sm">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center font-medium">
                    {i + 1}
                  </span>
                  <span className="pt-0.5">{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function DimensionCard({ score }: { score: QualityScore }) {
  const [expanded, setExpanded] = React.useState(false);
  const scorePercent = Math.round(score.score * 100);
  
  const getScoreColor = (s: number) => {
    if (s >= 0.7) return 'text-green-500';
    if (s >= 0.5) return 'text-amber-500';
    return 'text-red-500';
  };

  const getBgColor = (s: number) => {
    if (s >= 0.7) return 'bg-green-500';
    if (s >= 0.5) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <Card className="flex flex-col h-full">
      <CardContent className="p-5 flex-1 flex flex-col">
        <div className="flex items-start justify-between mb-2">
          <h4 className="font-semibold">{DIMENSION_LABELS[score.dimension]}</h4>
          {score.passed ? (
            <CheckCircle2 className="w-5 h-5 text-green-500" />
          ) : (
            <XCircle className="w-5 h-5 text-red-500" />
          )}
        </div>
        
        <div className="flex items-center gap-3 mb-4">
          <div className="h-2 flex-1 bg-muted rounded-full overflow-hidden">
            <div 
              className={`h-full ${getBgColor(score.score)}`} 
              style={{ width: `${scorePercent}%` }}
            />
          </div>
          <span className={`text-sm font-bold ${getScoreColor(score.score)}`}>
            {scorePercent}%
          </span>
        </div>

        <div className="text-sm text-muted-foreground flex-1">
          <p className={expanded ? '' : 'line-clamp-2'}>
            {score.feedback}
          </p>
          
          {expanded && score.suggestions.length > 0 && (
            <div className="mt-3 space-y-2">
              <span className="font-medium text-foreground text-xs uppercase tracking-wider">Suggestions</span>
              <ul className="list-disc pl-4 space-y-1">
                {score.suggestions.map((sug, i) => (
                  <li key={i}>{sug}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <button 
          onClick={() => setExpanded(!expanded)}
          className="text-xs font-medium text-primary flex items-center gap-1 mt-4 hover:underline"
        >
          {expanded ? (
            <>Read less <ChevronUp className="w-3 h-3" /></>
          ) : (
            <>Read more <ChevronDown className="w-3 h-3" /></>
          )}
        </button>
      </CardContent>
    </Card>
  );
}
