import { ImagePromptItem } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Copy, Image as ImageIcon, Sparkles } from 'lucide-react';

export function ImagePromptsSection({ prompts }: { prompts: ImagePromptItem[] }) {
  const copyToClipboard = (prompt: string) => {
    navigator.clipboard.writeText(prompt);
  };

  return (
    <div className="space-y-6">
      <div className="bg-muted/50 border border-primary/20 rounded-lg p-4 flex items-start gap-4">
        <div className="bg-primary/20 p-2 rounded-full text-primary mt-1">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h4 className="font-semibold text-sm mb-1">How to use these prompts</h4>
          <p className="text-sm text-muted-foreground">
            Copy these prompts into AI image generators like Midjourney, DALL·E 3, or Stable Diffusion to create visuals that match your brand identity and campaign strategy.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {prompts.map((item, idx) => (
          <Card key={idx} className="bg-card shadow-sm flex flex-col">
            <CardHeader className="pb-3 border-b">
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg flex items-center gap-2">
                  <ImageIcon className="w-4 h-4 text-muted-foreground" />
                  {item.use_case}
                </CardTitle>
                <Badge variant="outline">{item.aspect_ratio}</Badge>
              </div>
              <div className="flex flex-wrap gap-2 mt-3">
                <Badge variant="secondary" className="text-xs">{item.platform}</Badge>
                <Badge variant="secondary" className="text-xs bg-muted">{item.style}</Badge>
                <Badge variant="secondary" className="text-xs bg-muted">{item.mood}</Badge>
              </div>
            </CardHeader>
            <CardContent className="pt-4 flex-grow">
              <div className="bg-muted/50 p-4 rounded-md font-mono text-sm leading-relaxed text-foreground/90 border border-border/50">
                {item.prompt}
              </div>
            </CardContent>
            <CardFooter className="pt-0">
              <Button 
                variant="default" 
                className="w-full"
                onClick={() => copyToClipboard(item.prompt)}
              >
                <Copy className="w-4 h-4 mr-2" />
                Copy Prompt
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
