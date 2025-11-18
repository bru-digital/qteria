# OAuth Setup Guide

This guide explains how to configure Microsoft Azure AD and Google OAuth 2.0 for Qteria authentication.

## Overview

Qteria supports three authentication methods:
1. **Microsoft OAuth** (Primary - for TÜV SÜD and most TIC notified bodies using Microsoft 365)
2. **Google OAuth** (Secondary - for organizations using Google Workspace)
3. **Email/Password** (Backwards compatibility)

## Prerequisites

- Admin access to Microsoft Azure Portal (for Microsoft OAuth)
- Admin access to Google Cloud Console (for Google OAuth)
- Qteria environment variables configured (`.env` file)

---

## Microsoft Azure AD OAuth Setup

### 1. Create Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Configure the registration:
   - **Name**: `Qteria Authentication`
   - **Supported account types**: `Accounts in this organizational directory only (Single tenant)`
   - **Redirect URI**:
     - Platform: `Web`
     - URL: `http://localhost:3000/api/auth/callback/microsoft` (development)
     - URL: `https://qteria.app/api/auth/callback/microsoft` (production)
5. Click **Register**

### 2. Get Client Credentials

1. On the app overview page, copy the **Application (client) ID**
2. Go to **Certificates & secrets** → **Client secrets** → **New client secret**
3. Add description: `Qteria Auth Secret`
4. Set expiration: `24 months` (recommended)
5. Click **Add** and copy the **Value** (this is your client secret)
6. **IMPORTANT**: Copy the secret immediately - it won't be shown again

### 3. Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Delegated permissions**
3. Add these permissions:
   - `User.Read` (Read user profile)
   - `profile` (View users' basic profile)
   - `email` (View users' email address)
   - `openid` (Sign users in)
4. Click **Add permissions**
5. Click **Grant admin consent for [Your Organization]** (requires admin role)

### 4. Add to Environment Variables

Add to your `.env` file:

```env
MICROSOFT_CLIENT_ID=your-application-client-id-here
MICROSOFT_CLIENT_SECRET=your-client-secret-value-here
```

### 5. Production Redirect URI

When deploying to production, add the production redirect URI:
1. Go to **Authentication** → **Platform configurations** → **Web**
2. Click **Add URI**
3. Add: `https://qteria.app/api/auth/callback/microsoft`
4. Click **Save**

---

## Google OAuth 2.0 Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Project name: `Qteria Authentication`
4. Click **Create**

### 2. Enable Google+ API

1. Navigate to **APIs & Services** → **Library**
2. Search for `Google+ API`
3. Click **Enable**

### 3. Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** user type (unless you have Google Workspace)
3. Click **Create**
4. Fill in the consent screen:
   - **App name**: `Qteria`
   - **User support email**: `support@qteria.com`
   - **App logo**: Upload your logo (120x120px PNG)
   - **Authorized domains**: `qteria.app`
   - **Developer contact email**: `support@qteria.com`
5. Click **Save and Continue**
6. **Scopes**: Add these scopes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `openid`
7. Click **Save and Continue**
8. **Test users** (for testing mode): Add test user emails
9. Click **Save and Continue**

### 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Configure the credentials:
   - **Application type**: `Web application`
   - **Name**: `Qteria Web App`
   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (development)
     - `https://qteria.app` (production)
   - **Authorized redirect URIs**:
     - `http://localhost:3000/api/auth/callback/google` (development)
     - `https://qteria.app/api/auth/callback/google` (production)
4. Click **Create**
5. Copy the **Client ID** and **Client secret**

### 5. Add to Environment Variables

Add to your `.env` file:

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

### 6. Publishing the App (Optional)

For production with >100 users:
1. Go to **OAuth consent screen**
2. Click **Publish App**
3. Submit for verification (takes 1-2 weeks)

For MVP/testing:
- Keep app in "Testing" mode (max 100 test users)
- Add test users manually in the OAuth consent screen

---

## Testing OAuth Integration

### 1. Start Development Server

```bash
cd apps/web
npm run dev
```

### 2. Test Microsoft OAuth

1. Navigate to `http://localhost:3000/login`
2. Click **Sign in with Microsoft**
3. You should be redirected to Microsoft login
4. Sign in with a test Microsoft account
5. Approve the consent screen
6. You should be redirected back to `/dashboard`

### 3. Test Google OAuth

1. Navigate to `http://localhost:3000/login`
2. Click **Sign in with Google**
3. You should be redirected to Google login
4. Sign in with a test Google account
5. Approve the consent screen
6. You should be redirected back to `/dashboard`

### 4. Error Handling

If you see an error:
- **`oauth_user_not_found`**: User email not in database. For MVP, users must be invited first.
- **`OAuthCallback Error`**: Check that redirect URIs match exactly (including http/https)
- **`Invalid client`**: Verify client ID and secret in `.env`

---

## Security Best Practices

### 1. Environment Variables

- **NEVER** commit `.env` to version control
- Use separate credentials for development and production
- Rotate client secrets every 6-12 months

### 2. OAuth Scopes

- Only request minimum required scopes: `openid`, `profile`, `email`
- Do NOT request sensitive scopes (calendar, contacts, etc.)

### 3. Token Storage

- OAuth tokens are stored server-side in Auth.js sessions
- Tokens are NOT exposed to the frontend
- Sessions use JWT with 7-day expiration

### 4. Multi-Tenancy

- OAuth users must have existing account in database (for MVP)
- Organization assignment happens during user invitation
- Future: implement organization assignment during OAuth sign-up

---

## Troubleshooting

### Microsoft OAuth Issues

**Error: AADSTS50011 - Reply URL mismatch**
- Check that redirect URI in Azure matches exactly: `http://localhost:3000/api/auth/callback/microsoft`
- Ensure you're using the correct environment (dev vs. production)

**Error: AADSTS65001 - User or admin has not consented**
- Go to Azure App Registration → API permissions
- Click **Grant admin consent for [Your Organization]**

**Error: invalid_client**
- Verify `MICROSOFT_CLIENT_ID` and `MICROSOFT_CLIENT_SECRET` in `.env`
- Check that client secret hasn't expired (Azure → Certificates & secrets)

### Google OAuth Issues

**Error: redirect_uri_mismatch**
- Check that redirect URI in Google Cloud Console matches: `http://localhost:3000/api/auth/callback/google`
- Authorized JavaScript origins must include base URL: `http://localhost:3000`

**Error: access_denied**
- User cancelled the consent screen
- Or user email is not in test users list (if app is in testing mode)

**Error: invalid_client**
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
- Check that OAuth client is enabled in Google Cloud Console

### General Auth.js Issues

**Error: NEXTAUTH_SECRET environment variable not set**
- Generate a secret: `openssl rand -base64 32`
- Add to `.env`: `NEXTAUTH_SECRET=your-generated-secret`

**Error: Cannot find module 'next-auth'**
- Run: `npm install next-auth`

**Session not persisting**
- Check that `NEXTAUTH_URL` matches your development URL
- Clear browser cookies and try again

---

## Production Deployment Checklist

- [ ] Create production Azure App Registration
- [ ] Create production Google Cloud project
- [ ] Update redirect URIs to production domain (`https://qteria.app`)
- [ ] Generate new client secrets for production
- [ ] Add production credentials to Vercel environment variables
- [ ] Test OAuth flows in production environment
- [ ] Enable monitoring for OAuth failures
- [ ] Set up alerts for high OAuth error rates
- [ ] Document OAuth credentials in password manager (1Password, LastPass)
- [ ] Rotate secrets every 6-12 months

---

## Support

For OAuth setup issues:
- **Microsoft Azure AD**: [Azure AD Documentation](https://learn.microsoft.com/en-us/azure/active-directory/)
- **Google OAuth**: [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- **Auth.js**: [NextAuth.js Documentation](https://next-auth.js.org/)

For Qteria-specific issues:
- Check logs: `apps/web/.next/server/app-paths-manifest.json`
- Enable debug mode: `NEXTAUTH_DEBUG=true` in `.env`
- Contact support: `support@qteria.com`
