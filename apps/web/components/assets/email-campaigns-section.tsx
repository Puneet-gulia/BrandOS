import { EmailCampaign } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Copy, Mail } from 'lucide-react';

export function EmailCampaignsSection({ emails }: { emails: EmailCampaign[] }) {
  const copyToClipboard = (email: EmailCampaign) => {
    const text = `Subject: ${email.subject_line}\nPreview: ${email.preview_text}\n\n${email.body}\n\nCTA: ${email.call_to_action_text}`;
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
      {emails.map((email, idx) => (
        <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
          {/* Timeline Node */}
          <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-background bg-primary text-primary-foreground font-bold shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
            {idx + 1}
          </div>
          
          <Card className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-card border-border shadow-sm p-0 overflow-hidden">
            <CardHeader className="bg-muted/40 border-b pb-4">
              <div className="flex justify-between items-start mb-2">
                <Badge variant="outline" className="bg-background">
                  {email.send_timing}
                </Badge>
                <Mail className="w-4 h-4 text-muted-foreground" />
              </div>
              <CardTitle className="text-lg">{email.name}</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              <div>
                <div className="text-xs font-semibold text-muted-foreground mb-1 uppercase tracking-wider">Subject</div>
                <div className="font-medium bg-background border p-2 rounded text-sm">{email.subject_line}</div>
              </div>
              <div>
                <div className="text-xs font-semibold text-muted-foreground mb-1 uppercase tracking-wider">Preview Text</div>
                <div className="text-sm text-muted-foreground italic">{email.preview_text}</div>
              </div>
              <div className="pt-2 border-t border-border/50">
                <div className="whitespace-pre-wrap text-sm leading-relaxed">{email.body}</div>
              </div>
              <div className="flex justify-center pt-2">
                <Button className="w-full sm:w-auto font-semibold">
                  {email.call_to_action_text}
                </Button>
              </div>
            </CardContent>
            <CardFooter className="bg-muted/20 border-t py-2">
              <Button 
                variant="ghost" 
                size="sm" 
                className="w-full flex justify-center text-muted-foreground hover:text-foreground"
                onClick={() => copyToClipboard(email)}
              >
                <Copy className="w-4 h-4 mr-2" />
                Copy Email
              </Button>
            </CardFooter>
          </Card>
        </div>
      ))}
    </div>
  );
}
