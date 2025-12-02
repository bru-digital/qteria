import { Metadata } from "next"
import Link from "next/link"

// Privacy Policy Configuration
const LAST_UPDATED_DATE = "January 20, 2025"

export const metadata: Metadata = {
  title: "Privacy Policy | Qteria",
  description: "Privacy policy and data protection practices for Qteria AI-powered document validation platform",
}

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/"
            className="text-blue-500 hover:text-blue-600 font-medium mb-4 inline-block"
          >
            ← Back to Home
          </Link>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
          <p className="text-sm text-gray-600">Last updated: {LAST_UPDATED_DATE}</p>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm p-6 md:p-8 space-y-8 print:shadow-none">

          {/* Introduction */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
            <p className="text-base text-gray-700 leading-relaxed">
              Qteria (&quot;we&quot;, &quot;us&quot;, &quot;our&quot;) is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered document validation platform for the Testing, Inspection, and Certification (TIC) industry.
            </p>
            <p className="text-base text-gray-700 leading-relaxed mt-3">
              This policy complies with the General Data Protection Regulation (GDPR) and other applicable data protection laws. By using Qteria, you consent to the data practices described in this policy.
            </p>
          </section>

          {/* Data Controller */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Data Controller Information</h2>
            {/* TODO: [BLOCKS PRODUCTION] Add full legal entity details required by GDPR Articles 13-14:
                - Full legal entity name (e.g., "Qteria Ltd.")
                - Registered company address (street, city, postal code, country)
                - Company registration number
                - Data Protection Officer contact (if applicable for companies >250 employees or high-risk processing)
                These details must be reviewed and approved by legal counsel before production launch. */}
            <p className="text-base text-gray-700 leading-relaxed">
              <strong>Company Name:</strong> Qteria<br />
              <strong>Email:</strong> privacy@qteria.com<br />
              <strong>Contact:</strong> For privacy-related inquiries, please email us at privacy@qteria.com
            </p>
          </section>

          {/* Personal Data Collected */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. Personal Data We Collect</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              We collect and process the following categories of personal data:
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.1 Account Information</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li>Email address</li>
              <li>Name</li>
              <li>Organization name and details</li>
              <li>User role (Process Manager, Project Handler, Administrator)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.2 OAuth Authentication Data</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li>Email address (from Microsoft/Google)</li>
              <li>Name (from Microsoft/Google)</li>
              <li>Profile picture (optional, from OAuth provider)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.3 Document Data</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li>Uploaded PDF and DOCX files (certification documents)</li>
              <li>Document metadata (filenames, upload timestamps, file sizes)</li>
              <li>Assessment results and validation criteria</li>
              <li>Evidence links (page numbers, section references)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.4 Usage and Activity Data</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li>Audit logs (login events, assessment actions, document uploads)</li>
              <li>Workflow creation and modification history</li>
              <li>Assessment execution timestamps and status</li>
            </ul>
          </section>

          {/* Legal Basis */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Legal Basis for Processing</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              Under GDPR Article 6, we process your personal data based on the following legal grounds:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li><strong>Contractual Necessity:</strong> Processing necessary to provide our document validation services</li>
              <li><strong>Legitimate Interest:</strong> Fraud prevention, security monitoring, and service improvement</li>
              <li><strong>Consent:</strong> Where you have explicitly consented to specific processing activities</li>
              <li><strong>Legal Obligation:</strong> Compliance with SOC2, ISO 27001, and other regulatory requirements</li>
            </ul>
          </section>

          {/* Data Processing & Storage */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Data Processing and Storage</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.1 Infrastructure and Services</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              We use the following trusted third-party services to process and store your data:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li><strong>Database:</strong> PostgreSQL hosted on Vercel/Neon (EU region recommended)</li>
              <li><strong>File Storage:</strong> Vercel Blob with AES-256 encryption at rest</li>
              <li><strong>Backend Hosting:</strong> Railway/Render for API services</li>
              <li><strong>Frontend Hosting:</strong> Vercel</li>
              <li><strong>Cache:</strong> Redis (ephemeral, no long-term storage)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.2 AI Processing - Zero Retention Agreement</h3>
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
              <p className="text-base text-gray-800 leading-relaxed">
                <strong>Important:</strong> We use Claude 3.5 Sonnet by Anthropic for AI validation with a <strong>zero-retention agreement</strong>. This means:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 mt-2 ml-4">
                <li>Your documents are <strong>never stored</strong> by Anthropic</li>
                <li>Document content is <strong>never used</strong> to train AI models</li>
                <li>AI processing is ephemeral (data deleted immediately after validation)</li>
                <li>Enterprise-grade privacy protection for confidential certification documents</li>
              </ul>
            </div>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.3 Security Measures</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li><strong>Encryption at Rest:</strong> All uploaded documents stored with AES-256 encryption (Vercel Blob)</li>
              <li><strong>Encryption in Transit:</strong> TLS 1.3 for all data transmission</li>
              <li><strong>Multi-Tenancy Isolation:</strong> Organization-level data separation (no data leakage between customers)</li>
              <li><strong>Role-Based Access Control (RBAC):</strong> User permissions enforced at database and API level</li>
              <li><strong>Audit Logging:</strong> All actions tracked with user context for security and compliance</li>
              <li><strong>Regular Security Assessments:</strong> SOC2 Type II certification pathway</li>
            </ul>
          </section>

          {/* Third-Party Services */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Third-Party Services and Data Sharing</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              We share data with the following trusted third-party service providers:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li><strong>Vercel:</strong> Frontend hosting, database, blob storage - <a href="https://vercel.com/legal/privacy-policy" className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">Privacy Policy</a></li>
              <li><strong>Railway/Render:</strong> Backend hosting - <a href="https://railway.app/legal/privacy" className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">Privacy Policy</a></li>
              <li><strong>Anthropic:</strong> AI validation with zero-retention agreement - <a href="https://www.anthropic.com/legal/privacy" className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">Privacy Policy</a></li>
              <li><strong>Microsoft/Google:</strong> OAuth authentication - Privacy policies: <a href="https://privacy.microsoft.com" className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">Microsoft</a>, <a href="https://policies.google.com/privacy" className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">Google</a></li>
            </ul>
            <p className="text-base text-gray-700 leading-relaxed mt-4">
              We do not sell or share your personal data with third parties for marketing purposes.
            </p>
          </section>

          {/* Data Retention */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Data Retention</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              We retain your data for the following periods:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li><strong>User Accounts:</strong> Retained while account is active; deleted within 30 days of account closure</li>
              <li><strong>PDF Documents:</strong> Retained for assessment duration + 90 days, then automatically deleted (configurable per organization)</li>
              <li><strong>Assessment Results:</strong> Retained indefinitely for audit trail (GDPR legitimate interest for compliance)</li>
              <li><strong>Audit Logs:</strong> Retained for 7 years (SOC2/ISO 27001 requirement)</li>
              <li><strong>AI Processing Data:</strong> <strong>Zero retention</strong> - documents never stored by Anthropic, deleted immediately after processing</li>
            </ul>
            <p className="text-base text-gray-700 leading-relaxed mt-4">
              You may request early deletion of your data by contacting privacy@qteria.com (subject to legal retention requirements).
            </p>
          </section>

          {/* User Rights */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Your Rights Under GDPR</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              Under GDPR Chapter III, you have the following rights regarding your personal data:
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">8.1 Right to Access</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You can request a copy of all personal data we hold about you, including account details, assessment history, and uploaded documents.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">8.2 Right to Rectification</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You can update your profile information, organization details, and account settings at any time through the platform.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">8.3 Right to Erasure (&quot;Right to be Forgotten&quot;)</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You can request deletion of your account and all associated data. We will delete your data within 30 days, subject to legal retention requirements (audit logs may be retained for 7 years for SOC2 compliance).
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">8.4 Right to Data Portability</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You can export your assessment results and workflow configurations in JSON or PDF format.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">8.5 Right to Object</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You can object to processing of your personal data for legitimate interests. We will cease processing unless we have compelling legitimate grounds.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">8.6 Right to Lodge a Complaint</h3>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              You have the right to lodge a complaint with your local data protection authority if you believe we have violated your privacy rights.
            </p>

            <p className="text-base text-gray-700 leading-relaxed mt-6 bg-gray-50 p-4 rounded">
              <strong>To exercise any of these rights, please contact us at:</strong> privacy@qteria.com
            </p>
          </section>

          {/* International Data Transfers */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. International Data Transfers</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              Your data may be processed in the European Union (EU) and the United States (US) depending on our service providers:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li><strong>Primary Data Processing:</strong> EU region (Neon PostgreSQL, Vercel EU hosting)</li>
              <li><strong>AI Processing:</strong> US (Anthropic - zero retention agreement applies)</li>
            </ul>
            <p className="text-base text-gray-700 leading-relaxed">
              For data transfers outside the EU, we use Standard Contractual Clauses (SCCs) approved by the European Commission to ensure adequate data protection.
            </p>
          </section>

          {/* Cookies & Tracking */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Cookies and Tracking</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              We use essential cookies to provide our services:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4 ml-4">
              <li><strong>Essential Cookies:</strong> Auth.js session token (httpOnly, secure, necessary for authentication)</li>
              <li><strong>Analytics Cookies:</strong> We do not currently use analytics or advertising cookies</li>
            </ul>
            <p className="text-base text-gray-700 leading-relaxed">
              You can disable cookies in your browser settings, but this may affect your ability to use the platform.
            </p>
          </section>

          {/* Changes to Policy */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Changes to This Privacy Policy</h2>
            <p className="text-base text-gray-700 leading-relaxed">
              We may update this Privacy Policy from time to time to reflect changes in our practices or legal requirements. We will notify you of material changes via email at least 30 days before they take effect. The &quot;Last Updated&quot; date at the top of this page indicates when the policy was last modified.
            </p>
            <p className="text-base text-gray-700 leading-relaxed mt-4">
              Continued use of Qteria after changes take effect constitutes acceptance of the updated Privacy Policy.
            </p>
          </section>

          {/* Contact */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Contact Us</h2>
            <p className="text-base text-gray-700 leading-relaxed mb-4">
              For privacy-related inquiries, questions about this policy, or to exercise your GDPR rights, please contact us:
            </p>
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-base text-gray-800">
                <strong>Email:</strong> <a href="mailto:privacy@qteria.com" className="text-blue-500 hover:underline">privacy@qteria.com</a><br />
                <strong>Company:</strong> Qteria<br />
                <strong>Response Time:</strong> We aim to respond to all privacy inquiries within 30 days
              </p>
            </div>
          </section>

        </div>

        {/* Footer Navigation */}
        <div className="mt-8 text-center">
          <Link
            href="/"
            className="text-blue-500 hover:text-blue-600 font-medium"
          >
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
