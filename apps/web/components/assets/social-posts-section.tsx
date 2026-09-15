import { SocialMediaPost } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Copy, Facebook, Instagram, Linkedin, Twitter } from 'lucide-react';
import { useState } from 'react';

export function SocialPostsSection({ posts }: { posts: SocialMediaPost[] }) {
  const platforms = Array.from(new Set(posts.map((p) => p.platform)));
  const [activePlatform, setActivePlatform] = useState(platforms[0] || '');

  const filteredPosts = posts.filter((p) => p.platform === activePlatform);

  const getPlatformIcon = (platform: string) => {
    const p = platform.toLowerCase();
    if (p.includes('facebook') || p.includes('fb')) return <Facebook className="w-5 h-5" />;
    if (p.includes('instagram') || p.includes('ig')) return <Instagram className="w-5 h-5" />;
    if (p.includes('linkedin') || p.includes('li')) return <Linkedin className="w-5 h-5" />;
    if (p.includes('twitter') || p.includes('x')) return <Twitter className="w-5 h-5" />;
    return <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-bold">{platform.charAt(0)}</div>;
  };

  const copyToClipboard = (content: string, hashtags: string[]) => {
    const text = `${content}\n\n${hashtags.join(' ')}`;
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2 mb-4 border-b pb-4">
        {platforms.map((platform) => (
          <Button
            key={platform}
            variant={activePlatform === platform ? 'default' : 'outline'}
            onClick={() => setActivePlatform(platform)}
            className="capitalize"
          >
            {getPlatformIcon(platform)}
            <span className="ml-2">{platform}</span>
          </Button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredPosts.map((post, idx) => (
          <Card key={idx} className="bg-card text-card-foreground shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="flex items-center space-x-2">
                {getPlatformIcon(post.platform)}
                <CardTitle className="text-sm font-medium capitalize">{post.platform}</CardTitle>
              </div>
              <Badge variant="secondary" className="capitalize">{post.post_type}</Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="whitespace-pre-wrap text-sm">{post.content}</p>
              
              <div className="flex flex-wrap gap-1">
                {post.hashtags.map((tag, i) => (
                  <Badge key={i} variant="outline" className="text-xs text-muted-foreground">{tag}</Badge>
                ))}
              </div>
              
              <div className="bg-muted p-3 rounded-md border border-border/50">
                <span className="text-xs font-semibold uppercase text-muted-foreground mb-1 block">Call to Action</span>
                <p className="text-sm">{post.call_to_action}</p>
              </div>
              
              {post.notes && (
                <p className="text-xs text-muted-foreground italic">Note: {post.notes}</p>
              )}
            </CardContent>
            <CardFooter>
              <Button 
                variant="ghost" 
                size="sm" 
                className="w-full flex items-center justify-center gap-2"
                onClick={() => copyToClipboard(post.content, post.hashtags)}
              >
                <Copy className="w-4 h-4" />
                Copy Post
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
