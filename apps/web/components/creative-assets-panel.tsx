'use client';

import { CampaignAssets } from '@/lib/types';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SocialPostsSection } from './assets/social-posts-section';
import { AdCopySection } from './assets/ad-copy-section';
import { EmailCampaignsSection } from './assets/email-campaigns-section';
import { LandingPageSection } from './assets/landing-page-section';
import { ImagePromptsSection } from './assets/image-prompts-section';
import { FileText, Image as ImageIcon, Layout, Mail, MessageSquare } from 'lucide-react';

export function CreativeAssetsPanel({ assets }: { assets: CampaignAssets }) {
  const hasSocial = assets.social_media_posts && assets.social_media_posts.length > 0;
  const hasAds = assets.ad_copy && assets.ad_copy.length > 0;
  const hasEmails = assets.email_campaigns && assets.email_campaigns.length > 0;
  const hasLandingPage = !!assets.landing_page_copy;
  const hasImagePrompts = assets.image_prompts && assets.image_prompts.length > 0;

  // Determine default tab
  let defaultTab = 'social';
  if (!hasSocial) {
    if (hasAds) defaultTab = 'ads';
    else if (hasEmails) defaultTab = 'emails';
    else if (hasLandingPage) defaultTab = 'landing-page';
    else if (hasImagePrompts) defaultTab = 'images';
  }

  if (!hasSocial && !hasAds && !hasEmails && !hasLandingPage && !hasImagePrompts) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-muted/20 border border-dashed rounded-lg">
        <FileText className="w-12 h-12 text-muted-foreground mb-4 opacity-50" />
        <h3 className="text-lg font-medium">No assets generated</h3>
        <p className="text-muted-foreground mt-2">There are no creative assets available for this campaign yet.</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <Tabs defaultValue={defaultTab} className="w-full">
        <TabsList className="mb-8 flex-wrap h-auto p-1 bg-muted/50 w-full justify-start">
          {hasSocial && (
            <TabsTrigger value="social" className="flex items-center gap-2 py-2.5">
              <MessageSquare className="w-4 h-4" />
              <span>Social Media</span>
            </TabsTrigger>
          )}
          {hasAds && (
            <TabsTrigger value="ads" className="flex items-center gap-2 py-2.5">
              <FileText className="w-4 h-4" />
              <span>Ad Copy</span>
            </TabsTrigger>
          )}
          {hasEmails && (
            <TabsTrigger value="emails" className="flex items-center gap-2 py-2.5">
              <Mail className="w-4 h-4" />
              <span>Emails</span>
            </TabsTrigger>
          )}
          {hasLandingPage && (
            <TabsTrigger value="landing-page" className="flex items-center gap-2 py-2.5">
              <Layout className="w-4 h-4" />
              <span>Landing Page</span>
            </TabsTrigger>
          )}
          {hasImagePrompts && (
            <TabsTrigger value="images" className="flex items-center gap-2 py-2.5">
              <ImageIcon className="w-4 h-4" />
              <span>Image Prompts</span>
            </TabsTrigger>
          )}
        </TabsList>

        <div className="mt-6 border border-border/40 rounded-xl bg-card/30 p-6 shadow-sm">
          {hasSocial && (
            <TabsContent value="social" className="mt-0 focus-visible:outline-none focus-visible:ring-0">
              <SocialPostsSection posts={assets.social_media_posts} />
            </TabsContent>
          )}

          {hasAds && (
            <TabsContent value="ads" className="mt-0 focus-visible:outline-none focus-visible:ring-0">
              <AdCopySection variants={assets.ad_copy} />
            </TabsContent>
          )}

          {hasEmails && (
            <TabsContent value="emails" className="mt-0 focus-visible:outline-none focus-visible:ring-0">
              <EmailCampaignsSection emails={assets.email_campaigns} />
            </TabsContent>
          )}

          {hasLandingPage && (
            <TabsContent value="landing-page" className="mt-0 focus-visible:outline-none focus-visible:ring-0">
              <LandingPageSection copy={assets.landing_page_copy!} />
            </TabsContent>
          )}

          {hasImagePrompts && (
            <TabsContent value="images" className="mt-0 focus-visible:outline-none focus-visible:ring-0">
              <ImagePromptsSection prompts={assets.image_prompts} />
            </TabsContent>
          )}
        </div>
      </Tabs>
    </div>
  );
}
