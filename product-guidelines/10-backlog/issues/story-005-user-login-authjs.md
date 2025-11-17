# [STORY-005] User Login with Auth.js

**Type**: Story
**Epic**: EPIC-02 (Authentication & Authorization)
**Journey Step**: Foundation (Secures Access)
**Priority**: P0 (Blocks All User Features)
**RICE Score**: 150 (R:100 × I:3 × C:100% ÷ E:2)

---

## User Value

**Job-to-Be-Done**: When users need to access the platform, they need secure login with email/password authentication, so they can protect their certification data and maintain session persistence.

**Value Delivered**: Secure user authentication with JWT sessions that persist across browser refreshes, enabling users to stay logged in while protecting sensitive certification documents.

**Success Metric**: Login success rate >95%, session persistence >99%.

---

## Acceptance Criteria

- [ ] Login page UI created (email + password fields, submit button)
- [ ] Auth.js (NextAuth) configured in Next.js application
- [ ] PostgreSQL database adapter configured for session storage
- [ ] Credentials provider configured for email/password login
- [ ] JWT tokens issued on successful login
- [ ] JWT stored in httpOnly cookie (not localStorage)
- [ ] Sessions persist across browser refreshes
- [ ] Logout endpoint invalidates session
- [ ] Login errors display user-friendly messages
- [ ] Protected routes redirect to login if not authenticated

---

## Technical Approach

**Tech Stack Components Used**:
- Frontend: Next.js 14+ (App Router), Auth.js (NextAuth v5)
- Session Storage: PostgreSQL (NextAuth Prisma adapter)
- Authentication: JWT (stored in httpOnly cookies)

**Auth.js Configuration** (`app/api/auth/[...nextauth]/route.ts`):
```typescript
import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import { PrismaAdapter } from "@auth/prisma-adapter"
import { prisma } from "@/lib/prisma"
import bcrypt from "bcrypt"

export const authOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    CredentialsProvider({
      name: "Email",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        // Validate credentials
        const user = await prisma.user.findUnique({
          where: { email: credentials.email },
          include: { organization: true }
        })

        if (!user || !user.password_hash) {
          throw new Error("Invalid credentials")
        }

        const valid = await bcrypt.compare(
          credentials.password,
          user.password_hash
        )

        if (!valid) {
          throw new Error("Invalid credentials")
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
          organizationId: user.organization_id
        }
      }
    })
  ],
  session: {
    strategy: "jwt",
    maxAge: 7 * 24 * 60 * 60 // 7 days
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role
        token.organizationId = user.organizationId
      }
      return token
    },
    async session({ session, token }) {
      session.user.id = token.sub
      session.user.role = token.role
      session.user.organizationId = token.organizationId
      return session
    }
  },
  pages: {
    signIn: "/login",
    error: "/login"
  }
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
```

**Login Page** (`app/login/page.tsx`):
```typescript
"use client"
import { signIn } from "next-auth/react"
import { useState } from "react"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    const result = await signIn("credentials", {
      email,
      password,
      redirect: false
    })

    if (result?.error) {
      setError("Invalid email or password")
    } else {
      router.push("/dashboard")
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit">Sign In</button>
    </form>
  )
}
```

**Protected Route Middleware** (`middleware.ts`):
```typescript
import { withAuth } from "next-auth/middleware"

export default withAuth({
  pages: {
    signIn: "/login"
  }
})

export const config = {
  matcher: ["/dashboard/:path*", "/workflows/:path*", "/assessments/:path*"]
}
```

**Database Schema Addition** (users table needs password_hash):
```sql
ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
```

---

## Dependencies

- **Blocked By**:
  - STORY-001 (Database Schema) - need users table
  - STORY-004 (FastAPI Infrastructure) - need backend ready for JWT validation
- **Blocks**:
  - STORY-007 (RBAC) - need authentication before authorization
  - EPIC-03 (Workflow Management) - need users logged in to create workflows

---

## Estimation

**Effort**: 2 person-days

**Breakdown**:
- Auth.js setup: 0.5 days (install, configure, database adapter)
- Login UI: 0.5 days (form, styling, error handling)
- JWT session logic: 0.5 days (callbacks, token payload)
- Testing: 0.5 days (login flow, session persistence)

---

## Definition of Done

- [ ] Auth.js installed and configured
- [ ] Login page accessible at `/login`
- [ ] User can log in with email/password
- [ ] JWT token issued and stored in httpOnly cookie
- [ ] Session persists across browser refreshes
- [ ] Invalid credentials show error message
- [ ] Protected routes redirect to login if not authenticated
- [ ] Logout endpoint (`/api/auth/signout`) invalidates session
- [ ] JWT payload includes: user_id, email, role, organization_id
- [ ] Security tests pass (httpOnly cookie, no XSS vulnerability)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Functional Tests**:
- [ ] Login with valid credentials → redirect to dashboard
- [ ] Login with invalid email → show error "Invalid email or password"
- [ ] Login with invalid password → show error
- [ ] Session persists across refresh (JWT valid for 7 days)
- [ ] Logout → session invalidated, redirect to login
- [ ] Access protected route without login → redirect to login

**Security Tests**:
- [ ] JWT stored in httpOnly cookie (not accessible via JavaScript)
- [ ] Cookie has Secure flag (HTTPS only)
- [ ] Cookie has SameSite=Lax (CSRF protection)
- [ ] Password never sent to frontend (only hash stored)
- [ ] JWT cannot be tampered with (signature validation)

**Integration Tests**:
- [ ] Login → call FastAPI endpoint with JWT → 200 OK
- [ ] Login → logout → call API with old JWT → 401 Unauthorized

---

## Risks & Mitigations

**Risk**: XSS attack steals JWT from localStorage
- **Mitigation**: Store JWT in httpOnly cookie (JavaScript cannot access)

**Risk**: CSRF attack using stolen cookie
- **Mitigation**: Use SameSite=Lax cookie attribute, implement CSRF tokens for state-changing operations

**Risk**: Sessions not persisting (database adapter misconfigured)
- **Mitigation**: Test thoroughly with PostgreSQL adapter, verify sessions table populated

**Risk**: Password stored in plaintext (security disaster)
- **Mitigation**: Hash passwords with bcrypt (salt rounds=10), never log passwords

---

## Notes

- This is the **gateway story** for all user features - no user-facing features work without login
- Use bcrypt for password hashing (NOT plain text, NOT MD5)
- JWT expires after 7 days → users must re-login (balance security vs UX)
- After completing this story, proceed to STORY-006 (Google OAuth) for enterprise SSO
- Consider password reset flow (STORY-006B) if users need to recover access
- Frontend login UI should match design system (STORY-006C for design polish)
