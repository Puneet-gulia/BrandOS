'use client';

import { LandingPageCopy } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Copy, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

export function LandingPageSection({ copy }: { copy: LandingPageCopy }) {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const copySection = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-12">
      {/* Hero Section */}
      <section className="text-center py-16 px-6 bg-gradient-to-b from-muted/50 to-background rounded-xl border relative group">
        <Button 
          variant="ghost" 
          size="icon" 
          className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={() => copySection(`${copy.hero_headline}\n${copy.hero_subheadline}\nCTA: ${copy.hero_cta}`)}
        >
          <Copy className="w-4 h-4" />
        </Button>
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6">{copy.hero_headline}</h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">{copy.hero_subheadline}</p>
        <Button size="lg" className="text-lg px-8 py-6 rounded-full">{copy.hero_cta}</Button>
      </section>

      {/* Social Proof */}
      <section className="relative group">
        <Button 
          variant="ghost" 
          size="icon" 
          className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={() => copySection(copy.social_proof_statement)}
        >
          <Copy className="w-4 h-4" />
        </Button>
        <div className="bg-primary/5 border border-primary/20 p-8 rounded-lg text-center">
          <p className="text-lg md:text-xl font-medium italic text-foreground/80">"{copy.social_proof_statement}"</p>
        </div>
      </section>

      {/* Value Props */}
      <section className="relative group">
        <Button 
          variant="ghost" 
          size="icon" 
          className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={() => copySection(copy.value_propositions.join('\n'))}
        >
          <Copy className="w-4 h-4" />
        </Button>
        <h2 className="text-2xl font-bold mb-6 text-center">Why choose us?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {copy.value_propositions.map((vp, idx) => (
            <Card key={idx} className="bg-card">
              <CardHeader>
                <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold mb-2">
                  {idx + 1}
                </div>
              </CardHeader>
              <CardContent>
                <p className="font-medium">{vp}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="relative group">
        <Button 
          variant="ghost" 
          size="icon" 
          className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={() => copySection(copy.feature_sections.map(f => `${f.title}\n${f.body}`).join('\n\n'))}
        >
          <Copy className="w-4 h-4" />
        </Button>
        <div className="space-y-8">
          {copy.feature_sections.map((feature, idx) => (
            <div key={idx} className={`flex flex-col md:flex-row gap-8 items-center ${idx % 2 !== 0 ? 'md:flex-row-reverse' : ''}`}>
              <div className="w-full md:w-1/2 aspect-video bg-muted rounded-lg flex items-center justify-center border border-dashed border-muted-foreground/30 text-muted-foreground">
                [Image Placeholder]
              </div>
              <div className="w-full md:w-1/2 space-y-4">
                <h3 className="text-2xl font-bold">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section className="max-w-2xl mx-auto relative group">
        <Button 
          variant="ghost" 
          size="icon" 
          className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity z-10"
          onClick={() => copySection(copy.faq.map(f => `Q: ${f.question}\nA: ${f.answer}`).join('\n\n'))}
        >
          <Copy className="w-4 h-4" />
        </Button>
        <h2 className="text-2xl font-bold mb-6 text-center">Frequently Asked Questions</h2>
        <div className="space-y-4">
          {copy.faq.map((item, idx) => (
            <div key={idx} className="border rounded-lg overflow-hidden">
              <button 
                className="w-full px-6 py-4 text-left flex justify-between items-center font-medium hover:bg-muted/50 transition-colors"
                onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
              >
                {item.question}
                {openFaq === idx ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
              </button>
              {openFaq === idx && (
                <div className="px-6 pb-4 pt-2 text-muted-foreground bg-muted/20 border-t">
                  {item.answer}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Closing */}
      <section className="text-center py-16 px-6 bg-primary text-primary-foreground rounded-xl relative group">
        <Button 
          variant="ghost" 
          size="icon" 
          className="absolute top-2 right-2 text-primary-foreground hover:bg-primary-foreground/20 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={() => copySection(`${copy.closing_headline}\nCTA: ${copy.closing_cta}`)}
        >
          <Copy className="w-4 h-4" />
        </Button>
        <h2 className="text-3xl md:text-4xl font-bold mb-8">{copy.closing_headline}</h2>
        <Button size="lg" variant="secondary" className="text-lg px-8 py-6 rounded-full">{copy.closing_cta}</Button>
      </section>
    </div>
  );
}
