import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
const articles = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/articles' }),
  schema: z.object({
    title: z.string(), summary: z.string(), category: z.string(),
    publishedAt: z.string(), sourceTitle: z.string(), sourceUrl: z.string().url(),
    reviewStatus: z.enum(['unreviewed', 'reviewed', 'sample']),
  }),
});
export const collections = { articles };
