import type { NextAuthConfig } from "next-auth"

/**
 * Base Auth.js configuration for Edge Runtime (middleware).
 * Contains ONLY JWT validation logic - NO database, NO bcrypt.
 *
 * This config is safe to use in Edge Runtime because it doesn't import:
 * - bcrypt (Node.js native modules)
 * - Prisma (Node.js runtime dependencies)
 * - Any other Node.js-specific libraries
 */
export const baseAuthConfig = {
  providers: [], // Empty array - providers added in full config
  session: {
    strategy: "jwt" as const,
    maxAge: 7 * 24 * 60 * 60 // 7 days
  },
  callbacks: {
    async jwt({ token, user }: { token: any; user: any }) {
      // Add custom fields to JWT on sign in
      if (user) {
        token.role = user.role
        token.organizationId = user.organizationId
      }
      return token
    },
    async session({ session, token }: { session: any; token: any }) {
      // Add custom fields to session
      if (session.user) {
        session.user.id = token.sub as string
        session.user.role = token.role as string
        session.user.organizationId = token.organizationId as string
      }
      return session
    }
  },
  pages: {
    signIn: "/login",
    error: "/login"
  },
  secret: process.env.NEXTAUTH_SECRET,
} satisfies NextAuthConfig
