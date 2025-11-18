import { PrismaClient } from '@prisma/client'
import { getEnv } from '@/lib/env'

// Validate DATABASE_URL is set at module load time
const DATABASE_URL = getEnv('DATABASE_URL')

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
    errorFormat: 'pretty',
  })

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
