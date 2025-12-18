import { auth } from '@/lib/auth-middleware'
export default auth

// Protect these routes
export const config = {
  matcher: ['/dashboard/:path*', '/workflows/:path*', '/assessments/:path*'],
}
