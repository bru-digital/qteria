# [STORY-006] Google OAuth Integration

**Type**: Story
**Epic**: EPIC-02 (Authentication & Authorization)
**Journey Step**: Foundation (Simplifies Onboarding)
**Priority**: P1 (Important for Enterprise SSO)
**RICE Score**: 128 (R:80 × I:2 × C:80% ÷ E:1)

---

## User Value

**Job-to-Be-Done**: When enterprise users (TÜV SÜD employees) need to access the platform, they want to sign in with their existing Google Workspace account, so they don't need to manage another password.

**Value Delivered**: Frictionless onboarding for enterprise users via Google OAuth, reducing signup friction and enabling SSO for organizations with Google Workspace.

**Success Metric**: OAuth login success rate >90%, 50%+ of users choose Google login over email/password.

---

## Acceptance Criteria

- [ ] "Sign in with Google" button on login page
- [ ] Google OAuth provider configured in Auth.js
- [ ] Google Cloud Console project created with OAuth 2.0 credentials
- [ ] OAuth callback URL configured (`/api/auth/callback/google`)
- [ ] User profile data fetched from Google (email, name, picture)
- [ ] New users auto-created in database on first Google login
- [ ] Existing users can link Google account to email/password account
- [ ] OAuth consent screen shows app name, logo, privacy policy link
- [ ] OAuth scopes limited to profile + email (no sensitive data)

---

## Technical Approach

**Tech Stack Components Used**:

- Frontend: Next.js, Auth.js (NextAuth)
- OAuth Provider: Google OAuth 2.0
- Google Cloud Console: OAuth credentials, consent screen

**Google OAuth Setup**:

1. Create project in Google Cloud Console
2. Enable Google+ API
3. Create OAuth 2.0 credentials (Client ID + Secret)
4. Configure consent screen (app name, logo, privacy policy)
5. Add authorized redirect URI: `https://qteria.app/api/auth/callback/google`

**Auth.js Configuration** (add to `route.ts`):

```typescript
import GoogleProvider from 'next-auth/providers/google'

export const authOptions = {
  // ... existing config
  providers: [
    CredentialsProvider({
      /* ... */
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          prompt: 'select_account', // Always show account picker
          access_type: 'offline',
          response_type: 'code',
        },
      },
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      // Auto-create user if first Google login
      if (account?.provider === 'google') {
        const existingUser = await prisma.user.findUnique({
          where: { email: profile.email },
        })

        if (!existingUser) {
          // Create new user (need organization assignment logic)
          // For MVP: assign to default organization or require invite
          return '/onboarding?step=organization'
        }
      }
      return true
    },
    // ... existing callbacks
  },
}
```

**Login Page Update** (`app/login/page.tsx`):

```typescript
"use client"
import { signIn } from "next-auth/react"

export default function LoginPage() {
  return (
    <>
      {/* Existing email/password form */}

      <div className="oauth-divider">
        <span>OR</span>
      </div>

      <button
        onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
        className="google-oauth-button"
      >
        <GoogleIcon />
        Sign in with Google
      </button>
    </>
  )
}
```

**Environment Variables** (`.env`):

```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
NEXTAUTH_URL=https://qteria.app
NEXTAUTH_SECRET=your-secret-key
```

**OAuth Scopes**:

- `openid` - User identity
- `profile` - Name, picture
- `email` - Email address

---

## Dependencies

- **Blocked By**:
  - STORY-005 (User Login) - need Auth.js configured first
- **Blocks**: Nothing (enhancement to existing login flow)

---

## Estimation

**Effort**: 1 person-day

**Breakdown**:

- Google Cloud Console setup: 0.25 days (project, OAuth credentials)
- Auth.js provider config: 0.25 days (add Google provider)
- UI update: 0.25 days (add Google button, styling)
- Testing: 0.25 days (OAuth flow, error handling)

---

## Definition of Done

- [ ] Google Cloud Console project created
- [ ] OAuth 2.0 credentials configured
- [ ] "Sign in with Google" button on login page
- [ ] Google OAuth flow completes successfully
- [ ] User profile data fetched (email, name, picture)
- [ ] New users auto-created in database on first login
- [ ] Existing users can log in via Google
- [ ] OAuth consent screen configured with app branding
- [ ] Error handling for OAuth failures (user cancels, invalid credentials)
- [ ] Google login tested with multiple accounts
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Functional Tests**:

- [ ] Click "Sign in with Google" → redirect to Google consent screen
- [ ] Approve consent → redirect to dashboard with active session
- [ ] User cancels consent → return to login with error message
- [ ] First-time Google user → auto-create user in database
- [ ] Existing user logs in with Google → session created, no duplicate user
- [ ] User profile picture displayed in dashboard (from Google)

**Security Tests**:

- [ ] OAuth token not exposed to frontend (stored server-side)
- [ ] Invalid OAuth callback → error, no session created
- [ ] OAuth state parameter validated (CSRF protection)

**Edge Cases**:

- [ ] Google login with email already registered via email/password → merge accounts
- [ ] Google login with email from different domain → handled gracefully (optional: restrict to specific domains for enterprise)

---

## Risks & Mitigations

**Risk**: User signs up with Google, then tries email/password with same email → duplicate account

- **Mitigation**: Check for existing email before creating user, merge accounts if email matches

**Risk**: OAuth credentials leaked (Client Secret exposed)

- **Mitigation**: Store in environment variables, never commit to git, rotate secrets if compromised

**Risk**: Google API rate limits exceeded

- **Mitigation**: Monitor API usage in Google Cloud Console, upgrade quota if needed

**Risk**: Organization assignment unclear for Google users (which org should they join?)

- **Mitigation**: For MVP, require invitation link with org_id, or show onboarding flow to select/create organization

---

## Notes

- Google OAuth is **lower priority than email/password** (P1 vs P0) but high value for enterprise users
- TÜV SÜD uses Google Workspace → Google login is critical for their adoption
- After OAuth working, consider adding Microsoft/Azure AD for other enterprises (STORY-006B)
- OAuth consent screen requires verification if >100 users (Google review process takes 1-2 weeks)
- For MVP, keep consent screen in "Testing" mode (max 100 test users)
- After completing this story, proceed to STORY-007 (RBAC)
