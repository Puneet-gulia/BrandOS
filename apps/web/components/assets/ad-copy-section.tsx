import { AdVariant } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Copy } from 'lucide-react';

export function AdCopySection({ variants }: { variants: AdVariant[] }) {
  const copyToClipboard = (variant: AdVariant) => {
    const text = `Headline: ${variant.headline}\n\nBody: ${variant.body}\n\nCTA: ${variant.call_to_action}`;
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="grid grid-cols-1 gap-6">
      {variants.map((variant, idx) => (
        <Card key={idx} className="bg-card shadow-sm border-border">
          <CardHeader className="pb-3 border-b flex flex-row items-center justify-between">
            <div className="flex gap-2">
              <Badge variant="default">{variant.platform}</Badge>
              <Badge variant="secondary">{variant.format}</Badge>
            </div>
            <div className="text-xs text-muted-foreground flex gap-3">
              <span>H: {variant.headline.length} chars</span>
              <span>B: {variant.body.length} chars</span>
            </div>
          </CardHeader>
          
          <CardContent className="pt-6 space-y-5">
            <div>
              <h3 className="text-xl font-bold leading-tight mb-2">{variant.headline}</h3>
              <p className="text-sm text-foreground/90 whitespace-pre-wrap">{variant.body}</p>
            </div>
            
            <div className="inline-block px-4 py-2 bg-primary text-primary-foreground rounded-md font-medium text-sm">
              {variant.call_to_action}
            </div>
            
            {variant.target_audience_note && (
              <p className="text-xs text-muted-foreground border-l-2 border-muted-foreground/30 pl-3">
                Targeting: {variant.target_audience_note}
              </p>
            )}
          </CardContent>
          
          <CardFooter className="bg-muted/50 border-t py-3">
            <Button 
              variant="outline" 
              size="sm" 
              className="ml-auto"
              onClick={() => copyToClipboard(variant)}
            >
              <Copy className="w-4 h-4 mr-2" />
              Copy Ad Text
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
