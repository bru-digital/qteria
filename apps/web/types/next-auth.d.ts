import NextAuth, { DefaultSession } from "next-auth"
import { JWT } from "next-auth/jwt"

declare module "next-auth" {
  interface Session {
    user: {
      id: string
      role: string
      organizationId: string
    } & DefaultSession["user"]
  }

  interface User {
    id: string
    email: string
    name: string | null
    role: string
    organizationId: string
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    role?: string
    org_id?: string
  }
}
